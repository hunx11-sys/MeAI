// shared composite layouts
module.exports = function(L){
  const {C, W, H, text, card, pill, icon, base, title, circle, notes, gradientBg, blob} = L;
  async function divider(p, num, name, sub, colors, emoji){
    const s = base(p, {noChrome:true});
    s.addImage({path: await gradientBg('div'+num, colors, 30), x:0,y:0,w:W,h:H});
    s.addImage({path: await blob('w'+num, 'FFFFFF'), x:8.8, y:-1.2, w:6.4, h:6.4});
    text(s, 0.9, 2.1, 4, 1.2, num, {fontSize:64, bold:true, color:C.white});
    text(s, 0.9, 3.35, 11, 0.9, name, {fontSize:40, bold:true, color:C.white});
    text(s, 0.9, 4.35, 11, 0.6, sub, {fontSize:17, color:'F0F4FF'});
    text(s, 9.9, 1.9, 2.6, 2.2, emoji, {fontSize:110, align:'center'});
    return s;
  }
  // key message band at bottom
  function band(s, p, y, msg, colorKey='blue', opt={}){
    const h = opt.h || 0.9;
    card(s,p,0.6,y,12.13,h,{fill: L.LIGHT[colorKey]||C.blueL, shadow:false});
    text(s, 0.95, y, 11.5, h, msg, {fontSize: opt.fontSize||14, bold:true, color: C[colorKey+'D']||C[colorKey], valign:'middle'});
  }
  // source line
  function source(s, t){ text(s, 0.6, H-0.72, 12, 0.28, '출처: '+t, {fontSize:8.5, color:C.g500}); }
  return { divider, band, source };
};
