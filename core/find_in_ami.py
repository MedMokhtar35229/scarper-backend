from django.http import HttpResponse
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
import bs4
import requests
from core.models import Champ, Filtre


def find_contenu_ami(id_user):   
    champs= Champ.objects.filter(id_user_id=id_user)
    session = requests.Session()
    retry = Retry(connect=10, backoff_factor=0)
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    end_of_search=1360
    liste_date_pub=[]
    liste_date_upd=[]
    description=[]
    des_satisfe=False
    i=0
    for p in range(end_of_search):
        print ("lien : "+str(p))
        recherche_ami =session.get('https://fr.ami.mr/Recherche-'+str(p))  
        #transformer le lien vers un text avec le parser lxml
        text_transforme=bs4.BeautifulSoup(recherche_ami.text, 'lxml')
        for lien in text_transforme.find_all('a'):  
            if 'Depeche' in lien.get('href'):
                lien='https://fr.ami.mr/'+lien.get('href')
                new=bs4.BeautifulSoup(session.get(lien).content.decode('utf-8','ignore'),'html.parser')                
                div = new.find('div',class_='item_intro') 
                if  len(str(div.get_text(strip=True)))>100:
                                        contenu=str(div.get_text()).lower()
                                        i+=1
                                        print("contenu N",i)
                                        NOChamp=0
                                        for (index,champ) in enumerate(champs,start=1):
                                            if(contenu.find(str(champ.contenu).lower())!=-1):
                                                print(contenu)
                                                IDMChamp=champ.id_modele_id  
                                                if (champ.id_modele_id == IDMChamp):
                                                    NOChamp+=1 
                                                    print('champ ', champ.name,' exite dans le filtre ',i)                       
                                                    if(NOChamp == Champ.objects.filter(id_modele_id =champ.id_modele_id).count()):
                                                        try:
                                                            Filtre.objects.create(id_modele_id=champ.id_modele_id, contenu=str(div.get_text()),id_user_id=id_user)
                                                            print('filtre ajoute') 
                                                        except:
                                                            print('deja ajoute')
                                                        
                                                        
                                            else:
                                                        print('Pas de modele pour ce contenu')
                               
                                   
                        
                                   
                                   
                            
                      



           



