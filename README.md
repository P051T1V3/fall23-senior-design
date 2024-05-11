# fall23-senior-design
An app for doctors to record patient appointment audio and get the appointment summary. 

* The application can record audio or take an audio file as input
* The file is sent to my server on HuggingFace which transcribes the audio using faster-whisper and sends the result back
* The returned transcript can then be summarized in a 'specific format' using the GPT-3-turbo-1106 model. The model has been fine-tuned with 10 transcript-summary pairs
* The specific format of the summary allows the app to seperate the different fields which can be used to fill out a health record template using docxtpl–streamlining the entire process.
* Once the transcript is retrieved from HuggingFace, it is possible to search within the audio recording using the search feature. By searching a word, you can find the sentence that the word has been used in and clicking the sentence plays back the segment of the audio that contains that sentence.

Sample Summary:

"""

Hasta Hikayesi:

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
Uygulanan Tedaviler: Burun spreyi reçetesi verildi, ameliyat önerisi yapıldı

"""

NOTE: The HuggingFace token, GPT model id and openai key has been removed so the application can currently only record audio and play it back.
