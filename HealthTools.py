from gradio_client import Client
from docxtpl import DocxTemplate
from codecs import decode
import openai
import time
import os

HF_TOKEN = ""
OPENAI_KEY = ""

def summarize_hf_tool(audio_path):
    id = ""
    client = Client(f"https://p051t1v3-health.hf.space/--replicas/{id}/", hf_token=HF_TOKEN)
    result = client.predict(audio_path, api_name="/predict")
    return result

def summarize_gpt_tool(transcript):
    openai.api_key = OPENAI_KEY
    start = time.time()
    model_id = ""
    try:
        response = openai.ChatCompletion.create(
            model=f"ft:gpt-3.5-turbo-1106:personal::{model_id}",
            messages=[
                {
                "role": "system",
                "content": """You act as a medical doctor that takes detailed notes for every appointment. Document medical information in a doctor patient dialogue in completely in Turkish!. Word errors due to transcription and wrong speaker assignment errors can be present in the given dialogue!! Your role is to carefully extract and organize this scattered medical information into a coherent summary in the following structure: 
Section 1: Patient's Main Complaint and Story 
Purpose: Capture the patient's Main Complaint and Narrative of patient's account and symptoms. This includes a comprehensive description of the main complaint, focusing on its onset, duration, characteristics, and circumstances of occurrence mentioned by them or answered to an inquiry by the doctor.
Section 2: Symptoms
Purpose: Document all symptoms related to the patients main complaint, both stated, inferred and ruled out. 
Section 3: Medical History
Purpose: Document all personal and familial medical history given in the dialogue both stated and ruled out. 
Subsections: 
Chronic Ilnesses: : Document chronic conditions like diabetes, hypertension, etc. Do not include one off illnesses such as a flu, diarrhea etc.
Surgeries and Past Illnesses: Document past surgical procedures and any known serious past illnesses or infections such as tuberculosis, hepatitis, etc. 
Previous Treatments: List any mentioned treatments the patient had related to their condition.
Medications: Document any medication used by the patient. 
Allergies: Document any known allergies (drugs, foods, environmental, etc)
Psychiatric and Neurological Conditions: Document any history of psychiatric illnesses (e.g., depression, anxiety, etc) and neurological conditions (e.g., epilepsy, stroke, etc).
Family Health History: Document health issues in the family, especially hereditary conditions like heart diseases, cancer, genetic disorders.
Lifestyle-Related Health Factors: Document lifestyle factors impacting health, like smoking, alcohol use, nutrition, exercise habits, occupation and stress factors, travel, living conditions, sexual activity/number of sexual partners/use of protection during sexual activity including amount if applicable.  
Section 4: Doctor's Evaluation
Purpose: Summarize the doctor's advice, assessments, and actions prescribed, as detailed in the dialogue. 
Subsections:
In-Office Clinical Examinations and Results & Future Diagnostic Tests and Examinations:
This section encompasses two key aspects of patient evaluation. The first part, In-Office Clinical Examinations and Results, details the physical examination and any immediate tests conducted during the office visit, including hands-on examinations and specific tests like pressure sensitivity, reflex testing, auscultation, palpation, or measurements performed. Each examination should be described and documented separately. If no in-office examinations are conducted, the notation "Belirtilmedi" should be used.
The second part, Future Diagnostic Tests and Examinations, refers to the tests and medical examinations that the doctor recommends for the patient to undergo after the office visit. This includes, but is not limited to, blood work, imaging studies (X-rays, MRIs, CT scans), and specialist referrals. These are intended for further diagnosis or treatment planning and are to be scheduled and conducted post-visit.
Administered Treatments: Information about treatments administered during the office visit. This might include procedures like wound dressing, immediate interventions such as nebulizer therapy for asthma, application of casts or splints, and instructions for continuing treatment at home, if applicable.
   
Summary Format:
Hasta Hikayesi
Şikayet: [Main Complaint]
Öykü: [Narrative of patient's account and symptoms]
Semptomlar ve Bulgular
Semptomlar: [Enumerate each identified symptom or condition, listed seperated by comma on a single line]
Olmayan Semptomlar: [Symptoms or conditions asked by doctor but negated by patient, listed seperated by a comma on a single line]
Medikal Geçmiş
Kronik Hastalıklar: [Document Chronic Illnesses Here]
Ameliyatlar ve Geçmiş Hastalıklar: [Document Surgeries and Past Illnesses here]
Geçmiş Tedaviler: [Document Previous Treatments here]
Kullanılan İlaçlar: [Document Medications here]
Alerji: [Document Allergies here]
Psikiyatrik ve Nörolojik Durumlar: [Document Psychiatric and Neurological Conditions here]
Aile Sağlık Geçmişi: [Document Family Health History here]
Yaşam Tarzı İle İlgili Sağlık Faktörleri: [Document Lifestyle-Related Health Factors here]
Doktor Değerlendirmesi
Ofis içi Testler ve Sonuçları: 
[Description: Describe In-Office Clinical Examination1 and its result here]
[Description: Describe In-Office Clinical Examination2 and its result here]
[For additional examinations, continue adding In-Office Clinical Examinations and their results as needed]
    
(Note: This list can be expanded or shrunk as required.)
İstenilen Tetkikler: [Document Future Diagnostic Test and Examinations here]
Uygulanan Tedaviler: [Document Administered Treatments here]
"""
                },
                {
                "role": "user",
                "content": transcript
                }
            ],
            temperature=0.3,
            max_tokens=2048,
            top_p=0.5,
            frequency_penalty=0,
            presence_penalty=0
            )
    except Exception as e:
        print(e)
        return "Please try running it again."
        
    print("GPT summarized in", time.time()-start, "seconds.")
    # Reformat the GPT output
    gpt_response = decode(str(response.choices[0].message), 'unicode_escape')
    summary = gpt_response.split("\"content\": \"")[1][:-3]
    return summary

def report_filler_tool(summary, template_path):
    
    tpl=DocxTemplate(template_path)
    doc_name = os.path.basename(os.path.normpath(template_path))

    key_info = dict()
    for info in [i for i in summary.split("\n") if i!=""]:
        if len(info.split(": "))==2:
            k,v = info.split(": ")
            k = k.lower().replace(" ","_")
            key_info[k] = v
    
    tpl.render(key_info)
    tpl.save(f"Filled_{doc_name}")


def search_tool(sentences, query):
    matches = list()
    if query == "": return matches
    
    #matches = [s for s in sentences if query.lower() in s["text"].lower()]

    for s in sentences:
        if query.lower() in s["text"].lower():
            matches.append(s)
    return matches
    # Output for debug
    result = ("""Hasta Hikayesi:
Şikayet: Kulak tıkanıklığı, boyun ağrısı, tiroid nodülü
Öykü: Hasta, sürekli olarak kulak tıkanıklığı yaşadığını ve bunun için arada temizletmeye gittiğini belirtmiştir. Ayrıca boyun ağrısı şikayetiyle bir boyun emarı çektirmiş ve emarda tiroid nodülü tespit edilmiştir. Hasta, annesinde guatr olduğunu ve ilaç kullandığını ancak ameliyat olmadığını belirtmiştir. Boyun ağrısı için emar çektirdiğinde fıtık gibi bir şey fark ettiğini ve altı milimetre boyutunda bir nodül görüldüğünü ifade etmiştir. Ayrıca, İngiltere'de staj yaparken kedilere karşı alerjik reaksiyon geliştirdiğini ve bu reaksiyonun geçmediğini, sürekli burun tıkanıklığı ve akıntısı yaşadığını belirtmiştir.

Semptomlar ve Bulgular:
Semptomlar: Kulak tıkanıklığı, boyun ağrısı, tiroid nodülü, burun tıkanıklığı, burun akıntısı
Olmayan Semptomlar: Bilinç kaybı, baş dönmesi, baş ağrısı, göz sulanması, ateş, öksürük, nefes darlığı, göğüs ağrısı, mide bulantısı, kusma, idrar problemleri, bağırsak sorunları, alerjik reaksiyon

Medikal Geçmiş:
Kronik Hastalıklar: Belirtilmedi
Ameliyatlar ve Geçmiş Hastalıklar: Belirtilmedi
Geçmiş Tedaviler: Kulak temizliği
Kullanılan İlaçlar: Belirtilmedi
Alerji: Kedilere karşı alerjik reaksiyon
Psikiyatrik ve Nörolojik Durumlar: Belirtilmedi
Aile Sağlık Geçmişi: Annede guatr hastalığı
Yaşam Tarzı İle İlgili Sağlık Faktörleri: Belirtilmedi

Doktor Değerlendirmesi:
Ofis içi Testler ve Sonuçları: 
•⁠  ⁠Kulak muayenesi yapıldı, kulak tıkanıklığı tespit edildi
•⁠  ⁠Boyun muayenesi yapıldı, boyun ağrısı ve tiroid nodülü tespit edildi
•⁠  ⁠Burun muayenesi yapıldı, burun tıkanıklığı ve akıntısı tespit edildi
İstenilen Tetkikler: Ultrason ve tiroid testleri istendi
Uygulanan Tedaviler: Burun spreyi reçetesi verildi, ameliyat önerisi yapıldı""","transcript", "'SPEAKER 1', 0.0, 2.0, ' Evet.', ['SPEAKER 1', 2.0, 4.0, ' Günaydın.', ['SPEAKER 1', 4.0, 6.0, ' İyi gece geçmiş olsun.', ['SPEAKER 1', 6.0, 8.0, ' Merhaba. Teşekkürler. Sağ olun.', ['SPEAKER 1', 8.0, 10.0, ' Ne şikayetin var?', ['SPEAKER 1', 10.0, 12.0, ' Benim göğsüm sağ tarafında bir ağrı var.', ['SPEAKER 1', 12.0, 14.0, ' Bir aydır devam ediyor.', ['SPEAKER 1', 14.0, 16.0, ' Yaklaşık.', ['SPEAKER 1', 16.0, 18.0, ' Başladığından beri biraz hafifleşti.', ['SPEAKER 1', 18.0, 20.0, ' Ama hala var.', ['SPEAKER 1', 20.0, 22.0, ' Derin nefes alırken ağrıyor.', ['SPEAKER 1', 22.0, 24.0, ' Esnerken falan ağrıyor.', ['SPEAKER 1', 24.0, 26.0, ' Hareketle ağrıtıyor.', ['SPEAKER 1', 26.0, 28.0, ' Böyle göğsümü öne doğru', ['SPEAKER 1', 28.0, 30.0, ' çıkarttığımda ağrılığını hissediyorum.', ['SPEAKER 1', 30.0, 32.0, ' Hafif.', ['SPEAKER 1', 32.0, 34.0, ' Öyle.', ['SPEAKER 2', 34.0, 36.0, ' Bir aydır var şikayetlerin. Öyle mi?', ['SPEAKER 1', 36.0, 38.0, ' Evet. Bir ay geçmiş.', ['SPEAKER 2', 38.0, 40.0, ' Yok. Olmadı. Daha önce.', ['SPEAKER 2', 40.0, 42.0, ' İlk kez bir ay önce böyle bir şikayet oldu.', ['SPEAKER 2', 42.0, 44.0, ' Bununla beraber bir öksürük var mı?', ['SPEAKER 1', 44.0, 46.0, ' Yok. Öksürüğüm yok.', ['SPEAKER 2', 46.0, 48.0, ' Bulantı, kusma. Yok.', ['SPEAKER 2', 48.0, 50.0, ' Göğs ağrına eşlik eden başka bir rahatsızlığın?', ['SPEAKER 1', 50.0, 52.0, ' Yok.', ['SPEAKER 2', 52.0, 54.0, ' Bu sıkışma yanma batma tarzında mı?', ['SPEAKER 2', 54.0, 56.0, ' Yoksa...', ['SPEAKER 2', 56.0, 58.0, ' Sürekli mi oluyor?', ['SPEAKER 1', 58.0, 60.0, ' Bıçak gibi saplanıp gidiyor mu?', ['SPEAKER 1', 60.0, 62.0, ' Derin nefes aldığımda', ['SPEAKER 1', 62.0, 64.0, ' bıçak gibi saplanıp gidiyor diyebilirim.', ['SPEAKER 2', 64.0, 66.0, ' Derin nefes aldığımda...', ['SPEAKER 2', 66.0, 68.0, ' Sancı gibi değil. Künt bir ağrı.', ['SPEAKER 1', 68.0, 70.0, ' Evet. Öyle.', ['SPEAKER 2', 70.0, 72.0, ' Kronik bir hastalığın var mı?', ['SPEAKER 2', 72.0, 74.0, ' Hayır. Yok.', ['SPEAKER 1', 74.0, 76.0, ' Her gün kullandığın bir ilaç. Daha önce olduğun bir ameliyat.', ['SPEAKER 1', 76.0, 78.0, ' Yok. Dizimden bir ameliyat olmuştum. O kadar.', ['SPEAKER 1', 78.0, 80.0, ' Peki.', ['SPEAKER 1', 80.0, 82.0, ' Sigara içiyor musun?', ['SPEAKER 1', 82.0, 84.0, ' Yok. Çok nadir.', ['SPEAKER 1', 84.0, 86.0, ' Hayır.', ['SPEAKER 2', 86.0, 88.0, ' Arada. Peki.', ['SPEAKER 1', 88.0, 90.0, ' Alerjim var mı?', ['SPEAKER 1', 90.0, 92.0, ' Kedi alerjim var.', ['SPEAKER 1', 92.0, 94.0, ' İlaçlara falan var mı?', ['SPEAKER 1', 94.0, 96.0, ' Yok. İlaç kullanmıyorum. Kedi alerjisiyle ilgili.', ['SPEAKER 1', 96.0, 98.0, ' Kedi alerjisinden birazcık', ['SPEAKER 1', 98.0, 100.0, ' bahsedeyim. Şey...', ['SPEAKER 1', 100.0, 102.0, ' Ben bu ağrı başlamadan önce', ['SPEAKER 1', 102.0, 104.0,  3 ay İngiltere'ye, ['SPEAKER 1', 104.0, 106.0, ' gitmiştim.', ['SPEAKER 1', 106.0, 108.0,  İngiltere'ye gidip döndükten sonra, ['SPEAKER 1', 108.0, 110.0, ' kedilerime olan alerjim...', ['SPEAKER 2', 110.0, 112.0, ' Şu an evimde 2 kedi var benim.', ['SPEAKER 2', 112.0, 114.0, ' Kedilerime olan', ['SPEAKER 1', 114.0, 116.0, ' alerjim bir kabardı.', ['SPEAKER 1', 116.0, 118.0, ' Normalde hiç', ['SPEAKER 1', 118.0, 120.0, ' hissetmezken alerji...', ['SPEAKER 2', 120.0, 122.0, ' Toza falan var mı alerjin?', ['SPEAKER 2', 122.0, 124.0, ' Herkeste olduğu kadar olabilir.', ['SPEAKER 2', 124.0, 126.0, ' Belki çok hafif.', ['SPEAKER 1', 126.0, 128.0, ' Belki çok hafif.', ['SPEAKER 1', 128.0, 130.0, ' Kedi alerjim var mı?', ['SPEAKER 2', 130.0, 132.0, ' Böyle bir antikor, sizde kedi alerjisi var dediler.', ['SPEAKER 2', 132.0, 134.0, ' Öyle bir şey oldu mu hiç?', ['SPEAKER 1', 134.0, 136.0, ' Yok. Ama var olduğu ortada.', ['SPEAKER 1', 136.0, 138.0, ' Peki. Ona rağmen besliyorsun.', ['SPEAKER 2', 138.0, 140.0, ' Temasın var.', ['SPEAKER 1', 140.0, 142.0, ' İlaç? Onu nasıl yönetiyorsun?', ['SPEAKER 1', 142.0, 144.0, ' İlaç kullanmıyorum. Dediğim gibi...', ['SPEAKER 1', 144.0, 146.0, ' Normalde çok hafifti', ['SPEAKER 1', 146.0, 148.0, ' ya da yok gibiydi.', ['SPEAKER 1', 148.0, 150.0, ' 3 ay ayrı kalınca...', ['SPEAKER 1', 150.0, 152.0, ' Ben çocukluğumdan beri hayvanlarla beraberim.', ['SPEAKER 1', 152.0, 154.0, ' 3 ay ayrı kalınca geri döndüğümde', ['SPEAKER 1', 154.0, 156.0, ' çok arttı', ['SPEAKER 2', 156.0, 158.0, ' semptomları.', ['SPEAKER 2', 158.0, 160.0, ' Üstüne bastırınca ağrıyor mu göğsün? Yok.', ['SPEAKER 1', 162.0, 164.0, ' Semptomları çok arttı.', ['SPEAKER 1', 164.0, 166.0, ' Fakat bir de', ['SPEAKER 1', 166.0, 168.0, ' aynı zamanda grip gibi bir şey de yaşadım.', ['SPEAKER 1', 168.0, 170.0, ' Aynı dönemde.', ['SPEAKER 1', 170.0, 172.0, ' Daha sonra', ['SPEAKER 1', 172.0, 174.0, ' tam geçmeyecek', ['SPEAKER 1', 174.0, 176.0, ' alerji derken', ['SPEAKER 1', 176.0, 178.0, ' bir anda geçti.', ['SPEAKER 2', 178.0, 180.0, ' Peki. Şu an zaten gündemimiz buradaydı herhalde.', ['SPEAKER 1', 180.0, 182.0, ' Değil mi? Nasıl yani?', ['SPEAKER 1', 182.0, 184.0, ' Göğüs ağrısı var.', ['SPEAKER 1', 184.0, 186.0, ' Alerjin yok şu an. Yok. Şu an geçti alerjim.', ['SPEAKER 1', 186.0, 188.0, ' Ama başladığı dönemde', ['SPEAKER 1', 188.0, 190.0, ' hem griptim', ['SPEAKER 1', 190.0, 192.0, ' böyle çok fazla hapşuruyordum, öksürüyordum', ['SPEAKER 1', 192.0, 194.0, ' hem alerjim vardı.', ['SPEAKER 1', 194.0, 196.0, ' Spor egzersizi yapıyordun göğüs ağrısı için.', ['SPEAKER 1', 196.0, 198.0, ' Yok egzersizi yapmıyorum.', ['SPEAKER 2', 198.0, 200.0, ' Spor. Son zamanlarda ters bir hareket', ['SPEAKER 2', 200.0, 202.0, ' yapmış olabilir misin?', ['SPEAKER 2', 202.0, 204.0, ' Basket oynarken, kardiyo fitness yaparken', ['SPEAKER 1', 204.0, 206.0, ' yapmışsan ya da', ['SPEAKER 2', 206.0, 208.0, ' deli uyuyan birimisin mesela?', ['SPEAKER 2', 208.0, 210.0, ' Yanlışlıkla buraya bir şey çarpmış olabilir misin?', ['SPEAKER 2', 210.0, 212.0, ' Bir travma ökün oldu mu göğüs ağrısıyla ilgili?', ['SPEAKER 1', 212.0, 214.0, ' Göğüs ağrısıyla ilgili bir travma', ['SPEAKER 1', 214.0, 216.0, ' olduğunu düşünmüyorum ama o çok', ['SPEAKER 1', 216.0, 218.0, ' hapşurduğum, öksürdüğüm zaman', ['SPEAKER 1', 218.0, 220.0, ' belki', ['SPEAKER 1', 220.0, 222.0, ' çok sert bir hapşurmayla', ['SPEAKER 1', 222.0, 224.0, ' böyle sağa falan dönerken', ['SPEAKER 1', 224.0, 226.0, ' hapşururken ufak bir', ['SPEAKER 1', 226.0, 228.0, ' acımış olabileceğini düşünüyorum.', ['SPEAKER 1', 228.0, 230.0, ' Tamam muayene edelim.', ['SPEAKER 1', 232.0, 234.0, ' Bunu da getirsem olur mu?', ['SPEAKER 1', 234.0, 236.0, ' Siz muayene sırasında ne yaptığınızı böyle', ['SPEAKER 1', 236.0, 238.0, ' sanki not alıyormuş gibi', ['SPEAKER 1', 238.0, 240.0, ' kafanızdan geçirdiğini söylersiniz.', ['SPEAKER 1', 240.0, 242.0, ' Genel anlamda bir pansiyonu', ['SPEAKER 1', 242.0, 244.0, ' ölçmemiz lazım.', ['SPEAKER 1', 244.0, 246.0, ' Tamam mı?', ['SPEAKER 1', 246.0, 248.0, ' Evet.', ['SPEAKER 1', 248.0, 250.0, ' Evet.', ['SPEAKER 1', 250.0, 252.0, ' Evet.', ['SPEAKER 1', 252.0, 254.0, ' Evet.', ['SPEAKER 1', 254.0, 256.0, ' Evet.', ['SPEAKER 1', 256.0, 258.0, ' Evet.', ['SPEAKER 1', 258.0, 260.0, ' Evet.', ['SPEAKER 1', 260.0, 262.0, ' Evet.', ['SPEAKER 1', 262.0, 264.0, ' Evet.', ['SPEAKER 1', 274.0, 276.0, ' Pansiyon', ['SPEAKER 1', 276.0, 278.0, ' 14-9', ['SPEAKER 1', 278.0, 280.0, ' 140-90 normalde üst sınırında', ['SPEAKER 1', 280.0, 282.0, ' bazen doktor', ['SPEAKER 1', 282.0, 284.0, ' ziyareti sırasında hafif yüksek çıkabilir.', ['SPEAKER 1', 284.0, 286.0, ' Bu bizim', ['SPEAKER 1', 286.0, 288.0, ' alışık olduğumuz bir durum.', ['SPEAKER 1', 288.0, 290.0, ' Şimdi bir ağız muayene yapalım.', ['SPEAKER 1', 290.0, 292.0, ' Gelenin dışarı çıkarıp ağ dersen', ['SPEAKER 1', 292.0, 294.0, ' daha iyi görünür.', ['SPEAKER 1', 294.0, 296.0, ' Çok güzel.', ['SPEAKER 1', 296.0, 298.0, ' Biraz geniz akışın var arada öksürüğün oluyor mu?', ['SPEAKER 1', 298.0, 300.0, ' Bu dönemde yok.', ['SPEAKER 2', 300.0, 302.0, ' Şimdi tam olarak göğsünün neresi ağrıyor', ['SPEAKER 1', 302.0, 304.0, ' bana gösterir misin?', ['SPEAKER 1', 304.0, 306.0, ' Sağ taraf orta kısmı burada.', ['SPEAKER 1', 306.0, 308.0, ' Bazen göğsümün ortağı da', ['SPEAKER 1', 308.0, 310.0, ' orta kısmına doğru kayabilir.', ['SPEAKER 1', 310.0, 312.0, ' Önce görüntüyle bakalım.', ['SPEAKER 1', 312.0, 314.0, ' Göğsümün yanında bir deken ya da herhangi bir', ['SPEAKER 1', 314.0, 316.0, ' travma benzer bir şey var mı? Görünen yok.', ['SPEAKER 1', 316.0, 318.0, ' Şimdi dokunalım.', ['SPEAKER 1', 318.0, 320.0, ' Var mı ağrı? Yok.', ['SPEAKER 1', 320.0, 322.0, ' Şu an fark ettiğim bir ağrı yok.', ['SPEAKER 1', 322.0, 324.0, ' Demek ki dış kısımla ilgili bir durum yok.', ['SPEAKER 1', 324.0, 326.0, ' Ama içeriden gelen bir şey olabilir.', ['SPEAKER 1', 326.0, 328.0, ' Tabii içeride kalbimiz,', ['SPEAKER 1', 328.0, 330.0, ' işte kaburga kemiklerimiz', ['SPEAKER 1', 330.0, 332.0, ' ve akciğerimiz var.', ['SPEAKER 1', 332.0, 334.0, ' Onlara da diğer yöntemlerimize bakacağız.', ['SPEAKER 1', 334.0, 336.0, ' Şimdi sırtını açarsan', ['SPEAKER 1', 336.0, 338.0, ' göğsünü ve sırtını', ['SPEAKER 1', 338.0, 340.0, ' dinleyip akciğer muayeneyi', ['SPEAKER 1', 340.0, 342.0, ' tamamlayalım. Pek durabilirsin.', ['SPEAKER 1', 342.0, 344.0, ' Kollarını yukarı kaldır.', ['SPEAKER 1', 344.0, 346.0, ' Evet.', ['SPEAKER 1', 346.0, 348.0, ' İki defa ver.', ['SPEAKER 1', 350.0, 352.0, ' Hızlı kuvvetle.', ['SPEAKER 1', 354.0, 356.0, ' Derin nefes alalım. Akciğerini dinleyelim.', ['SPEAKER 1', 376.0, 378.0, ' Evet.', ['SPEAKER 1', 378.0, 380.0, ' Devam edelim.', ['SPEAKER 1', 380.0, 382.0, ' Göğsündeki akciğer bölgeni dinleyelim.', ['SPEAKER 1', 382.0, 384.0, ' Ön taraftan dinleyelim.', ['SPEAKER 1', 384.0, 386.0, ' Şimdi nefesini tut.', ['SPEAKER 1', 386.0, 388.0, ' Göğsünde kalp seslerini dinleyeyim.', ['SPEAKER 1', 396.0, 398.0, ' Bırakabilirsin.', ['SPEAKER 1', 398.0, 400.0, ' Kalp sesleri gayet normal.', ['SPEAKER 1', 400.0, 402.0, ' Akciğer sesi gayet normal.', ['SPEAKER 1', 402.0, 404.0, ' Şimdi uzanırsan', ['SPEAKER 1', 404.0, 406.0, ' karını muayene edelim.', ['SPEAKER 1', 408.0, 410.0, ' Dizlerini yükebilirsin.', ['SPEAKER 1', 410.0, 412.0, ' Karnını sıçacağız.', ['SPEAKER 1', 412.0, 414.0, ' Doğru değil.', ['SPEAKER 1', 414.0, 416.0, ' Evet.', ['SPEAKER 1', 416.0, 418.0, ' Karnı açalım.', ['SPEAKER 1', 418.0, 420.0, ' Görüntüde bir şey yok.', ['SPEAKER 1', 420.0, 422.0, ' Şimdi dokunarak, kalpe ederek', ['SPEAKER 1', 422.0, 424.0, ' herhangi bir anormallik', ['SPEAKER 1', 424.0, 426.0, ' var mı?', ['SPEAKER 1', 426.0, 428.0, ' Bakıyoruz. Ne yok?', ['SPEAKER 1', 428.0, 430.0, ' Yine bağırsak seslerini', ['SPEAKER 1', 430.0, 432.0, ' dinliyoruz.', ['SPEAKER 1', 434.0, 436.0, ' Evet.', ['SPEAKER 1', 438.0, 440.0, ' Bağırsak sesleri aktif.', ['SPEAKER 1', 440.0, 442.0, ' Normal düzeyde.', ['SPEAKER 1', 442.0, 444.0, ' Karı ciğer ve akciğerin', ['SPEAKER 1', 444.0, 446.0, ' dalağının olduğu yerleri kontrol ediyoruz.', ['SPEAKER 1', 446.0, 448.0, ' Onlarda da herhangi bir', ['SPEAKER 1', 448.0, 450.0, ' büyüklük, anormallik yok.', ['SPEAKER 1', 450.0, 452.0, ' Gayet sağlıklı', ['SPEAKER 1', 452.0, 454.0, ' görünüyorsun.', ['SPEAKER 1', 454.0, 456.0, ' Hidranın dayağına var mı?', ['SPEAKER 1', 456.0, 458.0, ' Yok.', ['SPEAKER 1', 458.0, 460.0, ' Evet.', ['SPEAKER 1', 460.0, 462.0, ' Göğüs ağrıda, nefes dağrıda', ['SPEAKER 1', 462.0, 464.0, ' eşlik ediyor mu?', ['SPEAKER 1', 464.0, 466.0, ' Nefes dağrıda eşlik eder.', ['SPEAKER 1', 468.0, 470.0, ' Nefes dağrı yok.', ['SPEAKER 1', 470.0, 472.0, ' Evet.', ['SPEAKER 2', 472.0, 474.0, ' Vücudunda bir morluk da görmüyorum.', ['SPEAKER 1', 474.0, 476.0, ' Hayır yok.', ['SPEAKER 2', 476.0, 478.0, ' Görüntüyle ilgili şeyler daha çok kalp ve', ['SPEAKER 2', 478.0, 480.0, ' akciğerle ilgili sorunlardan kaynaklanır.', ['SPEAKER 2', 480.0, 482.0, ' Bazen o bölgede kas ve kalorgalar', ['SPEAKER 1', 482.0, 484.0, ' olduğu için travmaya bağlı', ['SPEAKER 2', 484.0, 486.0, ' şeyler de olabilir.', ['SPEAKER 2', 486.0, 488.0, ' Buna yönelik olarak', ['SPEAKER 2', 488.0, 490.0, ' bir takım tetkikler isteyeceğiz.', ['SPEAKER 2', 490.0, 492.0, ' Sağlıklı.', ['SPEAKER 2', 492.0, 494.0, ' Acaba bu içeride iç organlardan mı', ['SPEAKER 1', 494.0, 496.0, ' kaynaklanıyor diye.', ['SPEAKER 1', 496.0, 498.0, ' Akciğer filmine bakacağız.', ['SPEAKER 2', 498.0, 500.0, ' Yine kalp ritmine bakalım.', ['SPEAKER 2', 500.0, 502.0, ' Kalbin atışıyla ilgili bir anormallik', ['SPEAKER 2', 502.0, 504.0, ' orada ağrı yapabilir.', ['SPEAKER 2', 504.0, 506.0, ' Yine damarlarla ilgili bir sorun yapabilir.', ['SPEAKER 2', 506.0, 508.0, ' Ama senin yaş grubunda ve ağrının', ['SPEAKER 2', 508.0, 510.0, ' karakterinde bu özellikler', ['SPEAKER 2', 510.0, 512.0, ' aslında yok. Ama yine de', ['SPEAKER 2', 512.0, 514.0, ' ekarte etmek için bu tarz tahminleri istiyoruz.', ['SPEAKER 2', 514.0, 516.0, ' Bir de kas enzimlerine', ['SPEAKER 2', 516.0, 518.0, ' bakacağım. Bazen o bölgedeki', ['SPEAKER 2', 518.0, 520.0, ' kaslarda bir yorgunluk, bir ağrı', ['SPEAKER 1', 520.0, 522.0, ' olduğu için de göğsün ağrıyabilir.', ['SPEAKER 2', 522.0, 524.0, ' Yakın zamanda geçirdiysen', ['SPEAKER 2', 524.0, 526.0, ' yani yakın zaman dediğim yine', ['SPEAKER 2', 526.0, 528.0, ' en az 2-3 hafta önce geçirilmiş', ['SPEAKER 2', 528.0, 530.0, ' bir solunum yolu iltihabın varsa', ['SPEAKER 2', 530.0, 532.0, ' bu öksürmeye bağlı olarak', ['SPEAKER 2', 532.0, 534.0, ' göğüs kaslarında ağrı yapabilir.', ['SPEAKER 2', 534.0, 536.0, ' Solunum kaslarından biri olduğu için', ['SPEAKER 1', 536.0, 538.0, ' göğüs kasları da.', ['SPEAKER 2', 538.0, 540.0, ' Bunları inceleyeceğiz.', ['SPEAKER 1', 540.0, 542.0, ' Bu üst solunum yolu enfeksiyonunu', ['SPEAKER 1', 542.0, 544.0, ' ben yaklaşık', ['SPEAKER 1', 544.0, 546.0, ' 2 ay önce geçirdim.', ['SPEAKER 1', 546.0, 548.0, ' Sağ göğsümün ortasındaki ağrı kaldı.', ['SPEAKER 1', 548.0, 550.0, ' Yani ondan beri.', ['SPEAKER 2', 550.0, 552.0, ' Evet. Bu ona bağlı bir şeyse', ['SPEAKER 2', 552.0, 554.0, ' bunun içeride bir', ['SPEAKER 2', 554.0, 556.0, ' iz düşümü var mı diye bakmak için', ['SPEAKER 2', 556.0, 558.0, ' röntgenini isteyebiliriz. Ama', ['SPEAKER 2', 558.0, 560.0, ' solunum seslerini dinlediğimde ben onunla', ['SPEAKER 2', 560.0, 562.0, ' ilgili bir kalıntı fark edemedim.', ['SPEAKER 2', 564.0, 566.0, ' Bundan sonraki aşamada', ['SPEAKER 2', 566.0, 568.0, ' tahlillerini, tetkiklerini değerlendirip', ['SPEAKER 2', 568.0, 570.0, ' sonuca gidebiliriz.', ['SPEAKER 1', 570.0, 572.0, ' Tetkik göğüs röntgeni olacak', ['SPEAKER 1', 572.0, 574.0, ' dediniz değil mi?', ['SPEAKER 1', 574.0, 576.0, ' Bir de kan testi galiba.', ['SPEAKER 1', 576.0, 578.0, ' Evet. Bir kan tali değil. Bir de EKG.', ['SPEAKER 2', 578.0, 580.0, ' EKG.', ['SPEAKER 2', 580.0, 582.0, ' En son kan talileri ne zaman', ['SPEAKER 2', 582.0, 584.0, ' yapılmıştı?', ['SPEAKER 2', 584.0, 586.0, ' Yaklaşık 1 ay önce', ['SPEAKER 1', 586.0, 588.0, ' yapıldı.', ['SPEAKER 1', 588.0, 590.0, ' Ama TSH sadece tiroid için', ['SPEAKER 1', 590.0, 592.0, ' kan talileri yaptırdım.', ['SPEAKER 1', 592.0, 594.0, ' Vitaminler bakılmadı. Hayır.', ['SPEAKER 1', 596.0, 598.0, ' Peki. Ben daha sonra', ['SPEAKER 2', 598.0, 600.0, ' farklı bir', ['SPEAKER 1', 600.0, 602.0, ' tahlil isteyeceğim şu an.', ['SPEAKER 1', 602.0, 604.0, ' Ona yönelik olarak', ['SPEAKER 1', 604.0, 606.0, ' kas enzimlerimize', ['SPEAKER 1', 606.0, 608.0, ' bakacağız. Bu bölgede ağrı yapan', ['SPEAKER 1', 608.0, 610.0, ' birinin var mı diye. Yine bir', ['SPEAKER 1', 610.0, 612.0, ' gizli bir iltihap var mı diye', ['SPEAKER 2', 612.0, 614.0, ' iltihabi markerlerine bakacağız.', ['SPEAKER 1', 628.0, 630.0, ' Ailede romatizmal bir hastalık var mı?', ['SPEAKER 1', 630.0, 632.0, ' Yok. Hayır.', ['SPEAKER 1', 632.0, 634.0, ' Romatizma hastalığı yok ailede.', ['SPEAKER 1', 636.0, 638.0, ' Kalp rahatsızlığı olan var mı?', ['SPEAKER 1', 638.0, 640.0, ' Yakınlarında?', ['SPEAKER 2', 640.0, 642.0, ' Var. Babam var.', ['SPEAKER 1', 642.0, 644.0, ' Birkaç yıl önce', ['SPEAKER 2', 646.0, 648.0, ' kalp', ['SPEAKER 2', 648.0, 650.0, ' rahatsızlığına', ['SPEAKER 1', 650.0, 652.0, ' ilgilenmişti.', ['SPEAKER 1', 652.0, 654.0, ' Babam', ['SPEAKER 1', 654.0, 656.0, ' kalp rahatsızlığı', ['SPEAKER 1', 656.0, 658.0, ' kalp krizi', ['SPEAKER 1', 658.0, 660.0, ' geçirmiş, fark etmemiş gibi bir', ['SPEAKER 1', 660.0, 662.0, ' olay oldu.', ['SPEAKER 1', 662.0, 664.0, ' Evet.', ['SPEAKER 2', 664.0, 666.0, ' Başka hastalığı var mı?', ['SPEAKER 1', 668.0, 670.0, ' Yüksek tansiyonu da var.', ['SPEAKER 1', 670.0, 672.0, ' Baba tarafında yüksek tansiyon var.', ['SPEAKER 1', 674.0, 676.0, ' Kolesterol de var sanırım.', ['SPEAKER 1', 676.0, 678.0, ' Bu yaşta olmasa da erkek cinsiyet,', ['SPEAKER 2', 678.0, 680.0, ' 40 yaş üstü olmak,', ['SPEAKER 1', 680.0, 682.0, ' ailede hipertansiyon ve kalp hastalığı', ['SPEAKER 1', 682.0, 684.0, ' ölçüsü bizim için çok önemli risk faktörleridir.', ['SPEAKER 2', 684.0, 686.0, ' O yüzden bir', ['SPEAKER 2', 686.0, 688.0, ' hasta bu sebeple gelmeyince bunları', ['SPEAKER 1', 688.0, 690.0, ' sorgulamamız gerekir.', ['SPEAKER 2', 698.0, 700.0, ' Ben sistemi aktarıyorum.', ['SPEAKER 2', 700.0, 702.0, ' Sekreterle görüşerek', ['SPEAKER 2', 702.0, 704.0, ' laboratuvarla diğer işlemlerini', ['SPEAKER 1', 704.0, 706.0, ' yaptırıp sonuçlarla', ['SPEAKER 1', 706.0, 708.0, ' tekrar haberleşelim.', ['SPEAKER 1', 708.0, 710.0, ' Tamam. Çok teşekkür ederim.'")