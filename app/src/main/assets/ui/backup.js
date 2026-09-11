'use strict';
const backupDialog=document.querySelector('#backupDialog');
document.querySelector('#openBackup').onclick=()=>{
 backupDialog.innerHTML=`<h2>${t("Kopia Twoich wspomnień")}</h2><p>${t("Jeden plik ZIP: wizyty, zdjęcia, oceny, własne listy i ustawienia.")}</p><button id="exportBackup">${t("Zapisz kopię")}</button><button id="importBackup">${t("Wczytaj kopię")}</button><p class="muted">${t("Wybierasz miejsce zapisu. Aplikacja nie wysyła kopii na serwer. Plik zawiera Twoje notatki i zdjęcia — przechowuj go w wybranym przez siebie miejscu.")}</p><div id="backupStatus" role="status"></div><button id="closeBackup">${t("Zamknij")}</button>`;
 document.querySelector('#closeBackup').onclick=()=>backupDialog.close();
 const run=action=>{if(!window.Passport?.[action]){document.querySelector('#backupStatus').textContent=t('Zapis i odczyt pliku są dostępne w aplikacji Android.');return;}document.querySelector('#exportBackup').disabled=true;document.querySelector('#importBackup').disabled=true;document.querySelector('#backupStatus').textContent=t('Wybierz plik w oknie telefonu…');window.Passport[action]();};
 document.querySelector('#exportBackup').onclick=()=>run('exportBackup');document.querySelector('#importBackup').onclick=()=>run('importBackup');backupDialog.showModal();
};
window.backupEvent=event=>{
 const status=document.querySelector('#backupStatus');if(!status)return;
 document.querySelector('#exportBackup').disabled=false;document.querySelector('#importBackup').disabled=false;
 if(event.type==='preview'){
  status.innerHTML=`<h3>${t("Podsumowanie kopii")}</h3><p>${t("Nowe wizyty: {n}",{n:event.newVisits})}<br>${t("Nowe listy: {n}",{n:event.newPlans})}<br>${t("Zdjęcia w kopii: {n}",{n:event.photos})}</p><p>${t("Pominięte istniejące wpisy: {visits}; listy: {plans}. Obecne wpisy zachowają swoje dane, również jeśli różnią się od kopii.",{visits:event.skippedVisits,plans:event.skippedPlans})}</p><p>${escapeHtml(t("Przywrócimy ustawienia z kopii: {theme}, kraj: {country}, język: {language}.",{theme:event.theme==='light'?'Light':'Dark',country:event.country==='PL'?t('Polska'):event.country==='DE'?t('Niemcy'):t('ekran główny'),language:LANGUAGES[event.language]||t('Zachowaj obecny język')}))}</p><button id="confirmBackupImport">${t("Połącz dane")}</button>`;
  document.querySelector('#confirmBackupImport').onclick=()=>{document.querySelector('#confirmBackupImport').disabled=true;document.querySelector('#exportBackup').disabled=true;document.querySelector('#importBackup').disabled=true;window.Passport.confirmImport(event.token);};
 }else{status.textContent=t(event.message||'');if(event.type==='imported'){localStorage.setItem('theme',event.theme);if(LANGUAGES[event.language])localStorage.setItem('language',event.language);sessionStorage.removeItem('country');setTimeout(()=>location.reload(),700);}}
};
