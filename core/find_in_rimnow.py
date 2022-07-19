import time
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from rest_framework.response import Response

import bs4
import requests
from core.models import Champ, Filtre


def find_contenu():               
    session = requests.Session()
    retry = Retry(connect=3, backoff_factor=0.5)
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('https://', adapter)
    session.mount('http://', adapter)

    premiere_page_rimnow =session.get('https://www.rimnow.mr/fr.html')   
    #transformer le lien vers un text avec le parser lxml
    text_transforme=bs4.BeautifulSoup(premiere_page_rimnow.text, 'lxml')
    #savoir capter tous les liens de tous les informations 
    imgs=[]
    #contenu=[]

    i=0
    champs= Champ.objects.all()
    for lien in text_transforme.find_all('a',target="_blank"): 
            
            try:          
              new=bs4.BeautifulSoup(requests.get(lien.get('href')).text,'html.parser')
              print(lien.get('href'))
            except:
              pass
            classes=["field-item even","tinymcewysiwyg","entry-content entry clearfix","content"]
            divs=['div','font']
            for div in new.find_all('div',class_=classes) :
                if div.img:
                    img=str(div.img['src'])
                    imgs.append(img)
                else:
                    try:
                        contenu=str(div.get_text(strip=True))
                        i+=1
                        print("contenu N",i)
                        NOChamp=0
                        for (index,champ) in enumerate(champs,start=1):     
                             if(contenu.find(champ.contenu)!=-1):
                                IDMChamp=champ.id_modele_id  
                                if (champ.id_modele_id == IDMChamp):
                                    NOChamp+=1 
                                    print('champ ', champ.name,' exite dans le filtre ',i)                       
                                    if(NOChamp == Champ.objects.filter(id_modele_id =champ.id_modele_id).count()):
                                          try:
                                           Filtre.objects.create(id_modele_id=champ.id_modele_id, contenu=contenu)
                                           print('filtre ajoute') 
                                          except:
                                            print('deja enregistre')
                                         
                                    else:
                                          print('Pas de modele pour ce contenu')
                    except:
                      pass   
      