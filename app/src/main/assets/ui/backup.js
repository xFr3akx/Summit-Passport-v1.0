'use strict';
const backupDialog=document.querySelector('#backupDialog');
document.querySelector('#openBackup').onclick=()=>{
 backupDialog.innerHTML='<h2>Kopia Twoich wspomnień</h2><p>Jeden plik ZIP: wizyty, zdjęcia, oceny, własne listy i ustawienia.</p><button id="exportBackup">Zapisz kopię</button><button id="importBackup">Wczytaj kopię</button><p class="muted">Wybierasz miejsce zapisu. Aplikacja nie wysyła kopii na serwer. Plik zawiera Twoje notatki i zdjęcia — przechowuj go w wybranym przez siebie miejscu.</p><div id="backupStatus" role="status"></div><button id="closeBackup">Zamknij</button>';
 document.querySelector('#closeBackup').onclick=()=>backupDialog.close();
 const run=action=>{if(!window.Passport?.[action]){document.querySelector('#backupStatus').textContent='Zapis i odczyt pliku są dostępne w aplikacji Android.';return;}document.querySelector('#exportBackup').disabled=true;document.querySelector('#importBackup').disabled=true;document.querySelector('#backupStatus').textContent='Wybierz plik w oknie telefonu…';window.Passport[action]();};
 document.querySelector('#exportBackup').onclick=()=>run('exportBackup');document.querySelector('#importBackup').onclick=()=>run('importBackup');backupDialog.showModal();
};
window.backupEvent=event=>{
 const status=document.querySelector('#backupStatus');if(!status)return;
 document.querySelector('#exportBackup').disabled=false;document.querySelector('#importBackup').disabled=false;
 if(event.type==='preview'){
  status.innerHTML=`<h3>Podsumowanie kopii</h3><p>Nowe wizyty: ${event.newVisits}<br>Nowe listy: ${event.newPlans}<br>Zdjęcia w kopii: ${event.photos}</p><p>Pominięte istniejące wpisy: ${event.skippedVisits}; listy: ${event.skippedPlans}. Obecne wpisy zachowają swoje dane, również jeśli różnią się od kopii.</p><p>Przywrócimy ustawienia z kopii: ${escapeHtml(event.theme==='light'?'Light':'Dark')}, kraj: ${escapeHtml(event.country||'ekran główny')}.</p><button id="confirmBackupImport">Połącz dane</button>`;
  document.querySelector('#confirmBackupImport').onclick=()=>{document.querySelector('#confirmBackupImport').disabled=true;document.querySelector('#exportBackup').disabled=true;document.querySelector('#importBackup').disabled=true;window.Passport.confirmImport(event.token);};
 }else{status.textContent=event.message||'';if(event.type==='imported'){localStorage.setItem('theme',event.theme);sessionStorage.removeItem('country');setTimeout(()=>location.reload(),700);}}
};
