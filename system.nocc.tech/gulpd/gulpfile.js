/*******************************************************************************
[install]
su -
yum -y install npm
node --version
	v6.16.0
↓
su app
cd /home/app/(HOSTNAME)/gulpd
npm init
	→ すべて Enter で進める → "package.json" が生成される
npm install --save-dev gulp gulp-plumber gulp-autoprefixer gulp-sass gulp-less gulp-stylus gulp-merge-media-queries gulp-csscomb gulp-clean-css gulp-concat gulp-uglify es6-promise
	→ 必要ファイルが "node_modules" 内に生成される
cat package.json
npm update
cat package.json
↓
mkdir -p ../gulpd.workspace/wch;chmod 777 ../gulpd.workspace/wch
mkdir -p ../gulpd.workspace/src;chmod 777 ../gulpd.workspace/src
mkdir -p ../gulpd.workspace/dst;chmod 777 ../gulpd.workspace/dst
↓
vi ./gulpfile.js
	当ファイルを設置する
↓
/usr/bin/node ./node_modules/gulp/bin/gulp.js
	→ 待ち受け状態になれば成功
	[00:00:00] Using gulpfile ~/(HOSTNAME)/gulpd/gulpfile.js
	[00:00:00] Starting 'default'...

[SyntaxError]
 	エラーが出たらバージョンを下げる 7.0->6.1
	npm uninstall -D gulp-autoprefixer
	npm install -D gulp-autoprefixer@6.1.0

[systemd]
vi /etc/systemd/system/gulpd.service
----------------------------------------
[Unit]
Description=gulpd

[Service]
WorkingDirectory=/home/app/(HOSTNAME)/gulpd
ExecStartPre=-/bin/rm -fr ../gulpd.workspace/*
ExecStartPre=-/bin/mkdir -p ../gulpd.workspace/dst
ExecStartPre=-/bin/mkdir -p ../gulpd.workspace/src
ExecStartPre=-/bin/mkdir -p ../gulpd.workspace/wch
ExecStartPre=-/bin/chmod -R 777 ../gulpd.workspace
ExecStart=/usr/bin/node ./node_modules/gulp/bin/gulp.js
User=app
Group=app
Restart=always
RestartSec=500ms
StartLimitInterval=0

[Install]
WantedBy=multi-user.target
----------------------------------------
systemctl daemon-reload
systemctl start gulpd
systemctl status gulpd
systemctl enable gulpd
systemctl is-enabled gulpd
*******************************************************************************/

require('es6-promise').polyfill();

var fs = require('fs');

var gulp = require('gulp');
var plumber = require('gulp-plumber');
var sass = require('gulp-sass');
var merge_media_queries = require('gulp-merge-media-queries');
var autoprefixer = require('gulp-autoprefixer');
var csscomb = require('gulp-csscomb');
var clean_css = require('gulp-clean-css');
var concat = require('gulp-concat');
var uglify = require('gulp-uglify');

gulp.task('default', function()
{
	//
	// workspace
	//
	var workspace = '../gulpd.workspace'
	//
	// gulp.watch()
	//
	gulp
		.watch(workspace + '/wch/*')
		.on('all', function(event, path) {
			console.log(event);
			console.log(path);
			compile(event, path);
		});
	// ------------------------------------------------------------------
	//
	// compile
	//
	function compile(event, path)
	{
		if (event!='add')
		{
			return;
		}
		//
		// wch/(hash).(ext)
		//
		var option = JSON.parse(fs.readFileSync(path, 'utf-8'));
		var _watch = path.split('/').slice(-1)[0].split('.')
		var hash = _watch[0];
		var ext = _watch[1];
		var dstDir = workspace + '/dst/' + hash;
		var dstFile = 'gulp.' + ext;
		//
		// onError()
		//
		function onError(error)
		{
			try
			{
				fs.writeFileSync(
					dstDir + '/' + dstFile,
					'@Error\n' + error.message
				);
			}
			catch (e)
			{
				console.log(e);
			}
		}
		//
		// css|js
		//
		if (ext=='css'
			|| ext=='sass'
			|| ext=='scss'
			|| ext=='less'
			|| ext=='styl')
		{
			//
			// css
			//
			// rootfile が指定時は rootfile だけをコンパイル対象にする。
			// 結果的に @import によって芋づる式にコンパイルされる。
			//
			// 行ずれ防止のため autoprefixer を sourcemap.init() より先に実行。
			// 他は実行順序に関係なく sourcemap に対して行ずれを発生させる。
			//
			var src = ('rootfile' in option)
				? workspace + '/src/' + hash + option['rootfile']
				: workspace + '/src/' + hash + '/**';
			var _gulp = gulp
				.src(src, {sourcemaps:option['sourcemaps']})
				.pipe(plumber({errorHandler:onError}))
			_gulp = (ext=='sass' || ext=='scss')
				? _gulp.pipe(sass({outputStyle:'expanded'}))
				: ext=='less'
					? _gulp.pipe(less())
					: ext=='styl'
						? _gulp.pipe(styl())
						: _gulp;
			_gulp = _gulp.pipe(concat(dstFile));
			_gulp = option['autoprefixer']
				? option['autoprefixer_browsers']
					? _gulp.pipe(autoprefixer({
						browsers:option['autoprefixer_browsers']}))
					: _gulp.pipe(autoprefixer())
				: _gulp;
			if (option['sourcemaps'])
			{
				//
				// ソースマップあり
				//
				return _gulp.pipe(gulp.dest(dstDir, {sourcemaps:'./'}));
			}
			else
			{
				//
				// ソースマップなし
				//
				if (option['merge_media_queries'])
				{
					_gulp = _gulp.pipe(merge_media_queries());
				}
				if (option['csscomb'])
				{
					_gulp = _gulp.pipe(csscomb());
				}
				if (option['clean_css'])
				{
					//
					// inline:['none'] オプションを指定すると clean-css は
					// .css に書かれた @import に対してエラーを吐かなくなる。
					//
					_gulp = _gulp.pipe(clean_css({inline:['none']}));
				}
				return _gulp.pipe(gulp.dest(dstDir));
			}
		}
		else if (ext=='js')
		{
			//
			// js
			//
			return gulp.src(workspace + '/src/' + hash + '/**')
				.pipe(plumber({errorHandler:onError}))
				.pipe(uglify())
				.pipe(concat(dstFile))
				.pipe(gulp.dest(dstDir));
		}
	}
});