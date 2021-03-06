# google_scholar_parser

Scripts to parse *"citations page"* of **Google Scholar**  

Using [scholar.py](https://github.com/ckreibich/scholar.py) v1.5.  

## Requirements
It runs in Python2.7 and requires the library BeautifulSoup (version3).
You can install BeautifulSoup using the command:

```shell
pip install -r requirements.txt
```

## Usage
Beware that Google might block you if you do too many requests in quick succession.   
You might want to use **tor** or **random sleep** times. For example:

```python
import time;  
random.seed();  
n = random.random()*5;  
time.sleep(n);  
```  

Get citations for a publication using its DOI:  
```shell
python scholar.py -c 1 10.1111/j.1096-3642.2009.00627.x
```

Output:  
```shell 
         Title The radiation of Satyrini butterflies (Nymphalidae: Satyrinae)...     
           URL http://onlinelibrary.wiley.com/doi/10.1111/j.1096-3642.2009.00627.x/full  
     Citations 14  
      Versions 6  
Citations list http://scholar.google.com/scholar?cites=13407052944292989945&as_sdt=2005&sciodt=0,5&hl=en&num=1  
 Versions list http://scholar.google.com/scholar?cluster=13407052944292989945&hl=en&num=1&as_sdt=0,5  
          Year 2011   
```

Grab the **Citations list** page:  
`http://scholar.google.com/scholar?cites=13407052944292989945`

And feed it to the script `scholar_cites.py`:
```shell
python scholar_cites.py http://scholar.google.com/scholar?cites=13407052944292989945
```

So you will get all the DOIs of publications citing your article (up to 100 DOIs):  
```shell
10.1111/j.1463-6409.2010.00421.x  
10.1146/annurev-ecolsys-102710-145024  
10.1111/j.1420-9101.2011.02352.x  
10.1111/j.1439-0469.2010.00587.x
```


