const _0xdb033c=_0x1aa8;function _0x1aa8(_0x57bda0,_0xfd7eb1){const _0x16728f=_0x1672();return _0x1aa8=function(_0x1aa8d4,_0x1bd09e){_0x1aa8d4=_0x1aa8d4-0x1ca;let _0x57b485=_0x16728f[_0x1aa8d4];return _0x57b485;},_0x1aa8(_0x57bda0,_0xfd7eb1);}(function(_0x47be50,_0x28ce56){const _0x36cf37=_0x1aa8,_0x563f74=_0x47be50();while(!![]){try{const _0x41d066=parseInt(_0x36cf37(0x1f1))/0x1+parseInt(_0x36cf37(0x1dc))/0x2+-parseInt(_0x36cf37(0x201))/0x3*(-parseInt(_0x36cf37(0x1cd))/0x4)+-parseInt(_0x36cf37(0x1f8))/0x5+-parseInt(_0x36cf37(0x208))/0x6+parseInt(_0x36cf37(0x1ec))/0x7*(-parseInt(_0x36cf37(0x209))/0x8)+parseInt(_0x36cf37(0x1ea))/0x9;if(_0x41d066===_0x28ce56)break;else _0x563f74['push'](_0x563f74['shift']());}catch(_0x30fa7e){_0x563f74['push'](_0x563f74['shift']());}}}(_0x1672,0x34c02));let mac=jz[_0xdb033c(0x20d)](_0xdb033c(0x1f7));mac==null&&(mac=randomString(0xc),jz[_0xdb033c(0x1d3)](_0xdb033c(0x1f7),mac,0x0));const APP_ID=_0xdb033c(0x1d6),APP_KEY=_0xdb033c(0x202),ERROR_MSG_CLOUDFLARE=_0xdb033c(0x1e6);function main(_0x5d8b05){const _0x1d24b4=_0xdb033c;if(!_0x5d8b05['hasOwnProperty'](_0x1d24b4(0x1fb))||!jz[_0x1d24b4(0x1df)])return{'error':_0x1d24b4(0x1f3)};return _0x5d8b05[_0x1d24b4(0x1e5)](_0x1d24b4(0x1f9))&&jz[_0x1d24b4(0x1fc)]({'proxy':_0x5d8b05[_0x1d24b4(0x1f9)]}),jz[_0x1d24b4(0x1cc)]==0x3?playlist(_0x5d8b05):play(_0x5d8b05);}function playlist(_0x532f6a){const _0x1ee2c9=_0xdb033c,_0x32ceb3=site+'/live.php?g=1';let _0x5505cd='',_0x2111a8=null;try{_0x5505cd=jz[_0x1ee2c9(0x1ce)](_0x32ceb3,getHeaders(APP_ID));if(_0x5505cd['includes'](_0x1ee2c9(0x1e1))&&_0x5505cd[_0x1ee2c9(0x1d8)]('cloudflare'))return{'error':ERROR_MSG_CLOUDFLARE};const _0x1517f7=JSON[_0x1ee2c9(0x1cb)](_0x5505cd);_0x2111a8=JSON[_0x1ee2c9(0x1cb)](aesDecrypt(_0x1517f7['sign'],_0x1517f7['iv']));}catch(_0x2231dd){return{'error':'\x22获取播放列表失败,\x20结果：'+_0x5505cd+_0x1ee2c9(0x1d1)+_0x2231dd['toString']()};}if(_0x2111a8[_0x1ee2c9(0x200)]==0x5e)return{'error':_0x2111a8[_0x1ee2c9(0x1f6)]};const _0x39eca5=getToken();jz['setCache']('ublive.token',_0x39eca5,0x3e8*0x3c*0x3c);let _0x2ef4dc=jz['getQuery'](_0x532f6a[_0x1ee2c9(0x1fb)],'cdn');_0x2ef4dc==null&&(_0x2ef4dc=_0x1ee2c9(0x1ee));const _0x3dfa46=[],_0xce12dc={};return _0x2111a8['return_live'][_0x1ee2c9(0x1d5)](_0x2a6ad6=>{const _0x3fd727=_0x1ee2c9,_0x16a91e={};_0x16a91e['name']=_0x2a6ad6[_0x3fd727(0x20b)],_0x16a91e['channels']=[],_0x2a6ad6['channel'][_0x3fd727(0x1d5)](_0x20354e=>{const _0x14c138=_0x3fd727,_0x22a1ab=_0x20354e[_0x14c138(0x1db)];let _0x53cba2=_0xce12dc[_0x22a1ab];if(_0x53cba2==null){const _0x340750={};_0x340750[_0x14c138(0x204)]=[],_0x340750[_0x14c138(0x20b)]=_0x20354e[_0x14c138(0x1d4)],_0xce12dc[_0x22a1ab]=_0x340750,_0x53cba2=_0x340750,_0x16a91e['channels'][_0x14c138(0x1e4)](_0x53cba2);}_0x53cba2['sources'][_0x14c138(0x1e4)]({'url':_0x14c138(0x1d7)+_0x20354e['id']+_0x14c138(0x1ca)+_0x2ef4dc,'js':jz[_0x14c138(0x1e7)]});}),_0x3dfa46[_0x3fd727(0x1e4)](_0x16a91e);}),{'groups':_0x3dfa46};}function _0x1672(){const _0x46cf95=['post','AES-128-CBC','return_txt','ublive.mac','259010fsSkYQ','proxy','cloudflare','url','setRequest','b6afab3d0fdf18096ce822cf39abed1b','substring','application/json;\x20charset=utf-8','return_code','174wfNjNp','W@ms7+2HZ34<iZz>','length','sources','return_token','armeabi-v7a','S900_Pro','2215104VPglDk','8KSdoxn','join','name','md5','getCache','&cdn=','parse','mode','16636wCewOm','get','327','getQuery',',\x20异常：','0123456789abcdefghijklmnopqrstuvwxyz','setCache','title','forEach','99185d988d8bd9d6acebc0af79d705c0','http://?id=','includes','opensslDecrypt','okhttp/3.12.0','cid','86196UxayoA','Gooooogle','00000000','rc4Decrypt','charAt','<html','stringify','/info.php?g=1','push','hasOwnProperty','无法访问安博服务器，cloudflare盾拦截，请更换网络环境','path','[null]','now','3414105UkJlKK','sign','2700453eDkDYr','/uri.php','z88','ublive.token','return_uri','359166HEpjGK','cdn','程序版本过低，请安装最新版本！！'];_0x1672=function(){return _0x46cf95;};return _0x1672();}function play(_0x2c7476){const _0x16e876=_0xdb033c,_0x2a8e1c=jz[_0x16e876(0x1d0)](_0x2c7476[_0x16e876(0x1fb)],'id'),_0x3c1127=jz[_0x16e876(0x1d0)](_0x2c7476[_0x16e876(0x1fb)],_0x16e876(0x1f2));let _0x165b3b=jz[_0x16e876(0x20d)](_0x16e876(0x1ef));_0x165b3b==null&&(_0x165b3b=getToken(),jz[_0x16e876(0x1d3)](_0x16e876(0x1ef),_0x165b3b,0x3e8*0x3c*0x3c));let _0x1c482f='';try{_0x1c482f=jz[_0x16e876(0x1f4)](site+_0x16e876(0x1ed),getHeaders(_0x165b3b),JSON[_0x16e876(0x1cb)](aesEncrypt(getId(_0x2a8e1c))));if(_0x1c482f[_0x16e876(0x1d8)](_0x16e876(0x1e1))&&_0x1c482f[_0x16e876(0x1d8)](_0x16e876(0x1fa)))return{'error':ERROR_MSG_CLOUDFLARE};const _0x2d9a92=JSON[_0x16e876(0x1cb)](_0x1c482f),_0x248144=JSON['parse'](aesDecrypt(_0x2d9a92[_0x16e876(0x1eb)],_0x2d9a92['iv']));if(_0x248144[_0x16e876(0x200)]==0x5e)return{'error':_0x248144[_0x16e876(0x1f6)]};const _0xcf3e39=_0x248144[_0x16e876(0x1f0)]['replace'](/z\d+\./,_0x3c1127+'.');return{'url':_0xcf3e39};}catch(_0x2a35c7){return{'error':_0x1c482f};}}const site='https://www.twtvcdn.com/ul02',indexMap={'0':0xa,'1':0xb,'2':0xc,'3':0xd,'4':0xe,'5':0xf,'6':0x10,'7':0x11,'8':0x12,'9':0x13,'a':0xa,'b':0xb,'c':0xc,'d':0xd,'e':0xe,'f':0xf,'g':0x10,'h':0x11,'i':0x12,'j':0x13,'k':0x14,'l':0x15,'m':0x16,'n':0x17,'o':0x18,'p':0x19,'q':0x1a,'r':0x1b,'s':0x1c,'t':0x1d,'u':0x1e,'v':0x1f,'w':0x20,'x':0x21,'y':0x22,'z':0x23,'A':0x24,'B':0x25,'C':0x26,'D':0x27,'E':0x28,'F':0x29,'G':0x2a,'H':0x2b,'I':0x2c,'J':0x2d,'K':0x2e,'L':0x2f,'M':0x30,'N':0x31,'O':0x32,'P':0x33,'Q':0x34,'R':0x35,'S':0x36,'T':0x37,'U':0x38,'V':0x39,'W':0x3a,'X':0x3b,'Y':0x3c,'Z':0x3d,'+':0x3e,'/':0x3f};function getToken(){const _0x1c9687=_0xdb033c,_0x65a63c=jz['get'](site+_0x1c9687(0x1e3),getHeaders(APP_ID)),_0x46bf20=JSON[_0x1c9687(0x1cb)](_0x65a63c),_0x117ff2=JSON[_0x1c9687(0x1cb)](aesDecrypt(_0x46bf20[_0x1c9687(0x1eb)],_0x46bf20['iv']));if(_0x117ff2[_0x1c9687(0x200)]==0x5e)throw new Error(_0x117ff2['return_txt']);return _0x117ff2[_0x1c9687(0x205)];}function getId(_0x59b451){const _0x1ad508=_0xdb033c;return JSON[_0x1ad508(0x1e2)]({'id':_0x59b451,'re':0x0});}function getHeaders(_0x521f9a){const _0x4a4c0d=_0xdb033c,_0x64420a='alps',_0x306887=_0x4a4c0d(0x207),_0x5a767f=JSON[_0x4a4c0d(0x1e2)]({'app_laguage':0x2,'brand':_0x64420a,'chip_id':'','chip_id2':_0x4a4c0d(0x1fd),'cpu_api':_0x4a4c0d(0x206),'cpu_api2':'armeabi','device_flag':'0','device_v_date':_0x4a4c0d(0x1cf),'mac':mac,'model':_0x306887,'model2':'','serial':getSerialMD5(_0x64420a,mac,_0x306887),'sun_xi_info':_0x4a4c0d(0x1e8),'time':Date[_0x4a4c0d(0x1e9)](),'token':_0x521f9a,'ubcode':_0x4a4c0d(0x1de)});return{'User-Agent':_0x4a4c0d(0x1da),'device_info':aesEncrypt(_0x5a767f),'content-type':_0x4a4c0d(0x1ff)};}function getSerialMD5(_0x591284,_0x1897b7,_0x439c2c){const _0x5ad990=_0xdb033c;return jz[_0x5ad990(0x20c)](jz['md5'](_0x591284+jz[_0x5ad990(0x20c)](_0x1897b7)+_0x439c2c+jz[_0x5ad990(0x20c)](_0x5ad990(0x1dd))+'201306@202106>')+'Ub');}function aesDecrypt(_0x169653,_0x30f7e8){const _0x2121c9=_0xdb033c,_0x24bcfd=indexMap[_0x169653['charAt'](_0x169653[_0x2121c9(0x203)]-0x6)],_0x407fcf=subDecryptStr(0x5,subDecryptStr(0xc,_0x169653[_0x2121c9(0x1fe)](_0x24bcfd),_0x30f7e8),_0x30f7e8);return jz[_0x2121c9(0x1d9)](_0x407fcf,_0x2121c9(0x1f5),APP_KEY,0x0,_0x30f7e8);}function subDecryptStr(_0x4e753e,_0x1f5d39,_0xcfa56c){const _0x5f0012=_0xdb033c,_0x339e56=parseInt(_0xcfa56c['charAt'](_0x4e753e),0xa)||0xa;return _0x1f5d39['substring'](0x0,_0x339e56)+_0x1f5d39[_0x5f0012(0x1fe)](_0x339e56*0x2);}function aesEncrypt(_0x352020){const _0x4bd3fc=_0xdb033c,_0x574d02=randomString(0x10),_0xb7f26a=jz['opensslEncrypt'](_0x352020,_0x4bd3fc(0x1f5),APP_KEY,0x0,_0x574d02),_0x14492f=subEncryptStr(0xc,subEncryptStr(0x5,_0xb7f26a,_0x574d02),_0x574d02),_0x54daeb=indexMap[_0x14492f[_0x4bd3fc(0x1e0)](_0x14492f[_0x4bd3fc(0x203)]-0x6)],_0x1bcb28=randomString(_0x54daeb);return JSON[_0x4bd3fc(0x1e2)]({'sign':_0x1bcb28+_0x14492f,'iv':_0x574d02});}function subEncryptStr(_0x35a5af,_0x28b79b,_0x1cbb0f){const _0x244e11=_0xdb033c,_0x1909d7=parseInt(_0x1cbb0f[_0x244e11(0x1e0)](_0x35a5af),0xa)||0xa,_0x254491=randomString(_0x1909d7);return _0x28b79b[_0x244e11(0x1fe)](0x0,_0x1909d7)+_0x254491+_0x28b79b[_0x244e11(0x1fe)](_0x1909d7);}function randomString(_0x33ffff){const _0x271b7b=_0xdb033c,_0x3cc88f=_0x271b7b(0x1d2);return Array['from']({'length':_0x33ffff},()=>_0x3cc88f[_0x271b7b(0x1e0)](Math['floor'](Math['random']()*_0x3cc88f[_0x271b7b(0x203)])))[_0x271b7b(0x20a)]('');}