const API_BASE='http://localhost:8000';
const COLORS=['#00B8D9','#FF8B00','#6554C0','#36B37E','#FF5630','#2684FF','#E83E8C','#7A869A','#FFC400','#00875A','#8777D9','#00A3BF'];
const aerialStyle={version:8,sources:{aerial:{type:'raster',tiles:[`${API_BASE}/api/basemap/{z}/{x}/{y}.png`],tileSize:256,minzoom:0,maxzoom:22,attribution:'Aerial imagery © LINZ CC BY 4.0'}},layers:[{id:'aerial',type:'raster',source:'aerial',minzoom:0,maxzoom:22}]};
const map=new maplibregl.Map({container:'map',style:aerialStyle,center:[175.47,-37.89],zoom:17,maxZoom:22});
map.addControl(new maplibregl.NavigationControl());
map.on('click',async event=>{
  if(map.getLayer('roofs')){const hit=map.queryRenderedFeatures(event.point,{layers:['roofs']})[0];if(hit){popup(event.lngLat,hit.properties);return}}
  const status=document.querySelector('#status');status.textContent='Finding building, LiDAR and roof planes…';document.querySelector('#result').replaceChildren();
  try{const response=await fetch(`${API_BASE}/api/roof-analysis`,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({lon:event.lngLat.lng,lat:event.lngLat.lat})});const data=await response.json();if(!response.ok)throw Error(data.detail||'Analysis failed');status.textContent=`Detected ${data.roof_faces.length} roof planes from ${data.lidar.point_count.toLocaleString()} LiDAR points.`;show(data)}catch(error){status.textContent=error.message}
});
function show(data){
  for(const id of ['building','roofs'])if(map.getLayer(id))map.removeLayer(id);for(const id of ['building','roofs'])if(map.getSource(id))map.removeSource(id);
  const features=data.roof_faces.map((face,index)=>({type:'Feature',geometry:face.geometry,properties:{...face,color:COLORS[index%COLORS.length]}}));
  map.addSource('roofs',{type:'geojson',data:{type:'FeatureCollection',features}});map.addLayer({id:'roofs',type:'fill',source:'roofs',paint:{'fill-color':['get','color'],'fill-opacity':.62,'fill-outline-color':'#fff'}});
  map.addSource('building',{type:'geojson',data:data.building.geometry});map.addLayer({id:'building',type:'line',source:'building',paint:{'line-color':'#e31b23','line-width':3}});renderResults(data.roof_faces)
}
function renderResults(faces){const result=document.querySelector('#result');result.replaceChildren();faces.forEach((face,index)=>{const card=document.createElement('button');card.className='face-card';card.innerHTML=`<span class="swatch" style="background:${COLORS[index%COLORS.length]}"></span><span class="face-title">Roof Plane ${face.id}</span><span class="direction">${face.direction}</span><dl><dt>Surface area</dt><dd>${face.area_m2.toFixed(1)} m²</dd><dt>Tilt</dt><dd>${face.tilt_deg.toFixed(1)}°</dd><dt>Azimuth</dt><dd>${String(Math.round(face.azimuth_deg)).padStart(3,'0')}°</dd><dt>Points</dt><dd>${face.point_count.toLocaleString()}</dd><dt>Fit RMSE</dt><dd>${face.fit_rmse.toFixed(3)} m</dd></dl>`;card.addEventListener('click',()=>{const center=geometryCenter(face.geometry);map.flyTo({center,zoom:Math.max(map.getZoom(),19)});popup({lng:center[0],lat:center[1]},face)});result.append(card)})}
function geometryCenter(geometry){const ring=geometry.type==='MultiPolygon'?geometry.coordinates[0][0]:geometry.coordinates[0];return ring.reduce((sum,point)=>[sum[0]+point[0]/ring.length,sum[1]+point[1]/ring.length],[0,0])}
function popup(lngLat,face){new maplibregl.Popup().setLngLat(lngLat).setHTML(`<strong>Roof Plane ${face.id}</strong><br>Area: ${Number(face.area_m2).toFixed(1)} m²<br>Tilt: ${Number(face.tilt_deg).toFixed(1)}°<br>Azimuth: ${String(Math.round(Number(face.azimuth_deg))).padStart(3,'0')}° (${face.direction})<br>Points: ${Number(face.point_count).toLocaleString()}<br>Fit RMSE: ${Number(face.fit_rmse).toFixed(3)} m`).addTo(map)}
