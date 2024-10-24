'''
NCBI REST API for https://eutils.ncbi.nlm.nih.gov/entrez/eutils
'''
import os
import time
import urllib.parse
import logging
import logging.config
import pandas as pd
from bs4 import BeautifulSoup
import requests
from pub_worm.impact_factor.impact_factor_lookup import get_impact_factor

try:
    logging.config.fileConfig('logging.config')
except Exception:
    pass

# Create a logger object
logger = logging.getLogger(__name__)

class EntrezAPI:

    def __init__(self):
        self.base_url_str = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
        self.max_retries = 3
        self.timeout = 20
        self.function = "esearch"
        self.api_key = os.environ.get('NCBI_API_KEY', None)


    def _rest_api_call(self, params, data=None):
        url_str = f"{self.base_url_str}/{self.function}.fcgi"
        params['retmode']='xml'

        if self.api_key:
            params['api_key'] = self.api_key

        query = '&'.join([f"{urllib.parse.quote(k, 'utf-8')}={urllib.parse.quote(v, 'utf-8')}" for k, v in params.items()])
        url_str = f"{url_str}?{query}"

        #self.max_retries = 3
        retry = 0
        done = False

        api_result = None
        api_error = "No Error Set"

        def handle_error(error_msg):
            print(error_msg)
            logger.debug(error_msg)
            nonlocal done, retry, api_error
            retry +=1
            if retry >= self.max_retries:
                done = True
                api_error = error_msg

        while not done:
            try:
                if data:
                    post_data = { "id": ",".join(data) } 
                    response = requests.post(url_str, data=post_data, timeout=self.timeout)
                else:
                    response = requests.get(url_str, timeout=self.timeout)

                response.raise_for_status()  # Check for HTTP errors
                if response.status_code == 200:
                    done = True
                    api_result = response.text
                elif response.status_code == 429:
                    handle_error(f"Request limiter hit. waiting 2 seconds [Retry: {retry + 1}] code: {response.status_code}")
                    time.sleep(2)
                else:
                    handle_error(f"Failed to retrieve data. | Retry- {retry +1} | Response code- {response.status_code}")

            except Exception as ex:
                aviod_logging_interpolation=f"Error while calling url_str {str(ex)}"
                logger.error(aviod_logging_interpolation)
                error_msg=f"Unexpected Error | Retry- {retry+1} | Response msg- {str(ex)}"
                if isinstance(ex, requests.exceptions.HTTPError):
                        error_msg = f"Check the format of the http request [Retry: {retry + 1}] code: {str(ex)}"
                elif isinstance(ex, requests.exceptions.ConnectionError):
                        error_msg = f"Connection Error [Retry: {retry + 1}] code: {str(ex)}"
                elif isinstance(ex, requests.exceptions.Timeout):
                        error_msg = f"Timeout Error [Retry: {retry + 1}] code: {str(ex)}"
                handle_error(error_msg)

        if api_result is None:
            api_result = f"<response><rest_api_error>{api_error}</rest_api_error></response>"

        if logger.isEnabledFor(logging.DEBUG):
            soup = BeautifulSoup(api_result, "xml")
            # Pretty-print the XML content
            pretty_data = soup.prettify()
            milliseconds = int(round(time.time() * 1000))
            timestamp_str = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) + f".{milliseconds % 1000:03d}"
            #with open(f"http_response-{timestamp_str}.xml", 'w') as file:
            #    file.write(pretty_data)
            logger.debug(pretty_data)

        return api_result


    def entreze_esearch(self, params):
        self.function="esearch"
        esearch_params = {}
        esearch_params['db']         = params.get('db', 'pubmed')
        esearch_params['retmax']     = params.get('retmax', '200')
        esearch_params['usehistory'] = "y"
        esearch_params['term']       = params.get('term', None)
        if esearch_params['term'] is None:
            logger.debug("Param 'searchTerm' is required but not passed.")

        api_result = self._rest_api_call(esearch_params)
        ret_params = self._history_key_to_json(api_result)
        return ret_params

    def entreze_epost(self, data, params={}):
        self.function="epost"
        epost_params = {}
        epost_params['db']     = params.get('db', 'pubmed')
        if data is None:
            logger.debug("Param 'data' is required but not passed.")

        api_result = self._rest_api_call(epost_params, data)
        ret_params = self._history_key_to_json(api_result)
        ret_params['count'] = len(data)
        ret_params['db'] =  epost_params['db']
        return ret_params

    def entreze_pmid_summaries(self, params):
        paper_summarys = []
        rec_count = int(params.get('count', 0))
        restart = 0
        while rec_count > 0 :
            params['retstart'] = str(restart)
            params['retmax']  = '200'
            
            soup = self._entreze_get_data(params, "esummary")
            if soup is None:
                return paper_summarys
            
            # Extract information for each UID
            for doc in soup.find_all("DocSum"):
                uid         = self._get_tag_text(doc, "Id")
                issn        = self._get_tag_text(doc, "Item", {"Name": "ISSN"})
                essn        = self._get_tag_text(doc, "Item", {"Name": "ESSN"})
                last_author = self._get_tag_text(doc, "Item", {"Name": "LastAuthor"})
                pmc_id      = self._get_tag_text(doc, "Item", {"Name": "pmc"})
                title       = self._get_tag_text(doc, "Item", {"Name": "Title"})
                source      = self._get_tag_text(doc, "Item", {"Name": "Source"})
                
                paper_summary = {
                    "uid"         : uid,
                    "issn"        : issn,
                    "essn"        : essn,
                    "last_author" : last_author,
                    "pmc_id"      : pmc_id,
                    "title"       : title,
                    "source"      : source
                }
                paper_summarys.append(paper_summary)
                
            restart   +=200 # Increment record position by 200
            rec_count -=200 # Pull the next 200 records or however many are remaining

        return paper_summarys

    def entreze_elink_pmid_to_pmcid(self, params):
        logger.debug("Entering entreze_elink_pmid_to_pmcid!!")
        self.function="elink"
        elink_results = []

        rec_count = int(params.get('count', 0))
        restart = 0
        entrez_params = {}
        entrez_params['dbfrom'] = 'pubmed'
        entrez_params['dbto'] = 'pmc'
        entrez_params['linkname'] = 'pubmed_pmc'

        required_params = ['query_key', 'WebEnv']
        for param_name in required_params:
            if param_name in params:
                entrez_params[param_name] = params[param_name]
            else:
                logger.debug(f"Param '{param_name}' is required but not passed")
                return None
            
        logger.debug(f"XXXXXXXX entreze_elink_pmid_to_pmcid '{rec_count}'")
        while rec_count > 0 :
            params['restart'] = restart

            api_result = self._rest_api_call(entrez_params)
            soup = BeautifulSoup(api_result, "xml")

            api_error = self._get_tag_text(soup,"rest_api_error")
            if api_error:
                logger.error("Error in entreze_elink_pmid_to_pmcid")
                # Maybe throw and exception here
                return None

            root_element = soup.find()
            if root_element.name == 'eLinkResult':
                logger.debug("root_element == eLinkResult!!")

                link_set_db = self._get_tag(soup, ['LinkSetDb'])
                if link_set_db:
                    id_elements = link_set_db.find_all('Id')
                    id_numbers = [id_element.get_text(strip=True) for id_element in id_elements]
                    # Get PubmedArticleSet
                    elink_results += id_numbers


            restart   +=200 # Increment record position by 200
            rec_count -=200 # Pull the next 200 records or however many are remaining
        
        return elink_results

    def entreze_efetch(self, params):
        logger.debug("Entering entreze_efetch!!")
        efetch_results = {'articles':[], 'references':[], 'authors':[]}

        rec_count = int(params.get('count', 0))
        restart = 0
        while rec_count > 0 :
            params['retstart'] = str(restart)
            params['retmax']  = '200'
            logger.debug(f"ZYYYYY {params} ")
            soup = self._entreze_get_data(params, "efetch")
            if soup is None:
                return efetch_results
            
            root_element = soup.find()
            if root_element.name == 'PubmedArticleSet':
                logger.debug("root_element == PubmedArticleSet!!")
                efetch_results['articles']   += self._get_pubmed_articles(soup)
                efetch_results['references'] += self._get_pubmed_references(soup)
                efetch_results['authors']    += self._get_pubmed_authors(soup)
            elif root_element.name == 'pmc-articleset':
                logger.debug("root_element == pmc-article set!!")
                pubmed_articles = self._get_pmc_articles(soup)
                # Get PubmedArticleSet
                efetch_results['articles'] += pubmed_articles

            restart   +=200 # Increment record position by 200
            rec_count -=200 # Pull the next 200 records or however many are remaining
        
        return efetch_results
    
    ############# entrez/eutils Helper funtions #############
    
    def _history_key_to_json(self, api_result):
        ret_params = {}
        ##ret_params['function'] = self.function
        # Parse the XML response using BeautifulSoup
        soup = BeautifulSoup(api_result, "xml")
        # Extract WebEnv and QueryKey
        count     = self._get_tag_text(soup, "Count")
        ret_max   = self._get_tag_text(soup, "RetMax")
        ret_start = self._get_tag_text(soup, "RetStart")
        web_env   = self._get_tag_text(soup, "WebEnv")
        query_key = self._get_tag_text(soup, "QueryKey")
        api_error = self._get_tag_text(soup, "rest_api_error")
        if count:
            ret_params['count'] = count
        if ret_max:
            ret_params['retmax'] = int(ret_max)
        if ret_start:
            ret_params['retstart'] = int(ret_start)

        ret_params['query_key'] = query_key
        ret_params['WebEnv']    = web_env
        if api_error:
            logger.error("Error in history_key_to_json")
            ret_params = {}
            ret_params["Error"] = api_error
        return ret_params


    def _get_pubmed_articles(self, soup):
        articles = []

        pubmed_articles = soup.find_all('PubmedArticle')
        # Iterate over the <PubmedArticle> elements
        for pubmed_article in pubmed_articles:
            logger.debug(f"_get_pubmed_articles  {pubmed_article}")
            article = {}
            medline_citation = self._get_tag(pubmed_article, ['MedlineCitation'])
            article_details  = self._get_tag(medline_citation, ['Article'])
            abstract_details = self._get_tag(article_details, ['Abstract'])
            journal          = self._get_tag(article_details, ['Journal'])
            pub_date         = self._get_tag(journal, ['JournalIssue', 'PubDate'])
            article_id_list  = self._get_tag(pubmed_article, ['PubmedData', 'ArticleIdList'])

            article['pmid']      = self._get_tag_text(medline_citation, "PMID")
            article['issn']      = self._get_tag_text(journal, "ISSN", {"IssnType": "Print"})
            article['eissn']     = self._get_tag_text(journal, "ISSN", {"IssnType": "Electronic"})
            article['pmc']       = self._get_tag_text(article_id_list, "ArticleId", {"IdType": "pmc"})
            article['doi']       = self._get_tag_text(article_id_list, "ArticleId", {"IdType": "doi"})
            article['pub_year']  = self._get_tag_text(pub_date, "Year")
            article['pub_month'] = self._get_tag_text(pub_date, "Month")
            article['pub_day']   = self._get_tag_text(pub_date, "Day")

            article['pub_abbr'] = self._get_tag_text(journal, "ISOAbbreviation")
            article['title']    = self._get_tag_text(article_details, "ArticleTitle")

            abstract_text = ""
            if abstract_details:
                abstract_text = abstract_details.get_text(separator=' ', strip=True)
            article['abstract']  = self._clean_data(abstract_text)

            if article['issn']:
                article['impact_factor'] = get_impact_factor(article['issn'])
            if 'impact_factor' not in article:
                article['impact_factor'] = get_impact_factor(article['eissn'])

            articles.append(article)

        return articles

    def _get_pubmed_authors(self, soup):
            authors = []

            pubmed_articles = soup.find_all('PubmedArticle')
            # Iterate over the <PubmedArticle> elements
            for pubmed_article in pubmed_articles:
                medline_citation = self._get_tag(pubmed_article, ['MedlineCitation'])

                source_pmid        = self._get_tag_text(medline_citation, "PMID")
                author_list     = self._get_tag(pubmed_article, ['AuthorList'])
                if author_list:
                    article_authors = author_list.find_all('Author')
                    for article_author in article_authors:
                        author = {'source_pmid':source_pmid}
                        author['last_name']  = self._get_tag_text(article_author, "LastName")
                        author['first_name'] = self._get_tag_text(article_author, "ForeName")
                        author['initials']   = self._get_tag_text(article_author, "Initials")
                        author['orcid']      = self._get_tag_text(article_author, "Identifier", {"Source": "ORCID"})

                        affiliation_info = self._get_tag(article_author, ['AffiliationInfo'])
                        author['affiliation'] = ''
                        if affiliation_info:
                            author['affiliation'] = self._get_tag_text(affiliation_info, "Affiliation")

                        authors.append(author)

            return authors

    def _get_pubmed_references(self, soup):
            references = []

            pubmed_articles = soup.find_all('PubmedArticle')
            # Iterate over the <PubmedArticle> elements
            for pubmed_article in pubmed_articles:
                medline_citation = self._get_tag(pubmed_article, ['MedlineCitation'])

                source_pmid        = self._get_tag_text(medline_citation, "PMID")
                reference_list     = self._get_tag(pubmed_article, ['ReferenceList'])
                if reference_list:
                    article_references = reference_list.find_all('Reference')
                    for article_reference in article_references:
                        reference = {'source_pmid':source_pmid}
                        reference['citation'] = self._get_tag_text(article_reference, "Citation")
                        article_id_list       = self._get_tag(article_reference, ['ArticleIdList'])
                        reference['pmid']     = self._get_tag_text(article_id_list, "ArticleId", {"IdType": "pubmed"})
                        reference['pmc']      = self._get_tag_text(article_id_list, "ArticleId", {"IdType": "pmc"})
                        references.append(reference)

            return references

    def _clean_data(self, data):
            data = data.encode("ascii", "ignore").decode()
            data = data.replace('\n',' ')
            data = data.replace('"','')
            data = data.replace("\x84", " ")
            return data
    
    def _get_pmc_articles(self, soup):
        
        articles = []
        pmc_articles = soup.find_all('article')
        for pmc_article in pmc_articles:
            #logger.debug(f"_get_pmc_articles  {pmc_article}")
            article = {}
            article['pmid']      = self._get_tag_text(pmc_article, 'article-id', {'pub-id-type': 'pmid'})
            article['pmcid']     = self._get_tag_text(pmc_article, 'article-id', {'pub-id-type': 'pmc'})
            article['publisher'] = self._clean_data(self._get_tag_text(pmc_article, "publisher-name"))
            article['title']      = self._clean_data(self._get_tag_text(pmc_article, "article-title"))
            article['abstract']  = self._clean_data(self._get_tag_text(pmc_article, "abstract"))
            
            body_tag = pmc_article.find('body')
            body_text = ""
            if body_tag:
                body_text = body_tag.get_text(separator=' ', strip=True)
            article['body']  = self._clean_data(body_text)
          
            articles.append(article)

        return articles



    def _entreze_get_data(self, params, function):
        """
        Helper function to call _rest_api_call

        Args:
        params: The parameter to be used to call entrez/eutils.
        function (str): The entrez function to call ['efetch' or 'esummary'].

        Returns:
            soup: Beautiful Soup Response XML

        Note: Both efetch and esummary use the same setup code before calling _rest_api_call
        """
        self.function = function
        entrez_params = {}
        entrez_params['db']  = params.get('db', 'pubmed')
        entrez_params['retmax']  = params.get('retmax', '200')
        entrez_params['retstart']  = params.get('retstart', '0')


        required_params = ['query_key', 'WebEnv']
        for param_name in required_params:
            if param_name in params:
                entrez_params[param_name] = params[param_name]
            else:
                logger.debug(f"Param '{param_name}' is required but not passed")
                return None

        api_result = self._rest_api_call(entrez_params)
        # Parse the XML response using BeautifulSoup
        soup = BeautifulSoup(api_result, "xml")

        api_error = self._get_tag_text(soup,"rest_api_error")
        if api_error:
            logger.error("Error in _entreze_get_data")
            # Maybe throw and exception here
            return None
        
        return soup
    
    ############# Beautiful Soup XML Helper funtions #############

    def _get_tag(self, soup, path_names):
        root = soup
        for path_name in path_names:
            #logger.debug(f"get_tag {type(root)} {root} {path_name}")
            root = root.find(path_name, default='')
        return root

    def _get_tag_text(self, soup, tag_name, attribute=None):
        ret_val = ""
        if soup is not None:
            try:
                if attribute:
                    tag = soup.find(tag_name, attribute)
                else:
                    tag = soup.find(tag_name)

                ret_val = tag.text if tag else ""
            except Exception as e:
                print(f"Error finding tag in _get_tag_text: {e}")
                ret_val = ""
        else:
            ret_val = ""

        return ret_val

