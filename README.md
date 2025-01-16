# 3DLNews-2.0: A Three-decade Dataset of US Local News Articles

## 1. Overview 
We present 3DLNews-2.0, an expanded version of the [3DLNews](https://github.com/wm-newslab/3DLNews) repository, featuring significant enhancements and broader coverage. Key highlights include:
- A collection of U.S. local news articles spanning nearly three decades, from 1995 to 2024.
- Over 8 million URLs (including HTML text), with a refined subset of more than 4 million filtered news article URLs.
- Coverage of article URLs from over 14,000 local newspapers, TV stations, and radio broadcasters across all 50 states, offering a comprehensive view of the U.S. local news landscape.
- Data gathered through an extended scraping process using Google and Twitter search results, building on the original 3DLNews scraping methodology.
- A rigorous multi-step filtering pipeline was employed to exclude non-news links and enhance the dataset with rich metadata, such as: names and geographic coordinates of the source media organizations, article publication dates and other relevant metadata.
- Demonstrated applications of the 3DLNews-2.0 dataset across four use cases, showcasing its versatility.
  
To cite, kindly use:

```
@inproceedings{ariyarathne_nwala_3dlnews,
  author    = {Gangani Ariyarathne and Alexander C. Nwala},
  title     = {3DLNews: A Three-decade Dataset of US Local News Articles},
  booktitle = {Proceedings of the 33rd ACM International Conference on Information and Knowledge Management (CIKM ’24)},
  year      = {2024},
  pages     = {1--5},
  location  = {Boise, ID, USA},
  publisher = {ACM},
  address   = {New York, NY, USA},
  doi       = {10.1145/3627673.3679165},
  url       = {https://doi.org/10.1145/3627673.3679165}
}
```

![\label{fig:3dln-v2}](img/3DLNews-V2.jpg)

Fig 1. Article Distribution Across US Counties in the 3DLNews-2.0 Dataset.

### 2. Accessing the Dataset

The dataset is publicly available for download via the following links. Please note that a Globus account is required to access the dataset.
- [3DLNews-2.0](https://app.globus.org/file-manager?origin_id=e524969c-7dff-474c-899c-efddf8d15b83&origin_path=%2F): Contains the dataset excluding the HTML files for the articles. The paths to the HTML files are included in the preprocessed article data objects, which is detailed in the "Data Enrichment" section.
- [3DLNews-2.0-HTML](https://app.globus.org/file-manager?origin_id=cbc9ee21-d7d3-4da6-ab27-d3f2360bdd79&origin_path=%2F): Includes the HTML files for the articles.

#### !!! Important Note
- The [3DLNews-2.0](https://app.globus.org/file-manager?origin_id=e524969c-7dff-474c-899c-efddf8d15b83&origin_path=%2F) dataset (without HTML) is approximately 2.8 GB.
- The [3DLNews-2.0-HTML](https://app.globus.org/file-manager?origin_id=cbc9ee21-d7d3-4da6-ab27-d3f2360bdd79&origin_path=%2F) (Only HTML files) dataset is approximately 247 GB.
  
Make sure to verify that you have sufficient storage and bandwidth before downloading.

## 3. 3DLNews-2.0 Dataset

### 3.1 Local news media dataset
We used an extended version of the Local Memory Project's (LMP) US local news dataset to get the local news media outlets. LMP's dataset consists of the websites of 5,993 local newspapers, 2,539 TV stations, and 1,061 radio stations, primarily extracted from [thepaperboy.com](thepaperboy.com) in 2016. We extended it by crawling and scraping [thepaperboy.com](thepaperboy.com) (again), [web.archive.org/web/20221203031956/http://www.usnpl.com/](web.archive.org/web/20221203031956/http://www.usnpl.com/), [50states.com](50states.com), and [einpresswire.com/world-media-directory/3/united-states](einpresswire.com/world-media-directory/3/united-states). Table 1 outline the number of local news media outlets that we have used to extract local news articles. The `broadcast` type refers to either TV or radio stations, because we could not accurately distinguish them during scraping.

The  improved local news media outlets dataset can be downloaded from here: [usa_2016_2024_pu5e.json.gz](https://github.com/wm-newslab/3DLNews/blob/main/resources/usa_2016_2024_pu5e.json.gz)

**Table 1:  US local news media dataset.**

| Media Type | Number of websites |
|------------|---------------------|
| Newspapers | 9,441               |
| Radio      | 2,449               |
| Broadcast  | 1,310               |
| TV         | 886                 |
| **Total**  | **14,086**          |

We issued Google and Twitter search queries to their respective search engines and scraped their links. For Google, we created queries from 1996 – 2024, for Twitter, 2006 – 2024. 

### 3.2 Data Filtering

The collected URLs from Google and Twitter scraping could include both news and non-news article links. Below, we outline our filtering process for removing non-news article URLs from 3DLNews. Since there is no universal standard URL format for news articles, we have also provided access to the raw data, allowing researchers to implement their own filtering methods. Our process was informed by an experiment in which we developed a gold-standard dataset of news article URLs to understand two key properties: **path depth** and **word-boundary**.

- **Path Depth**: The path depth of a URL refers to the number of hierarchies in its path property. For example:
  - `https://example.com/` has a path depth of 0.
  - `https://example.com/foo` has a path depth of 1.
  - `https://example.com/foo/bar` has a path depth of 2.
  
- **Word-Boundary**: A word-boundary is a symbol that separates words in a URL. For example:
  - In the URL `https://example.com/this-is-a-page`, the word-boundary is `-`.

### Filtering Process

The filtering process consisted of the following steps:

1. **Dereferencing URLs**: 
   - All URLs were dereferenced to resolve redirects and retrieve their final forms.

2. **Domain Matching**:
   - Links with domains not present in our local news media dataset were discarded.

3. **Normalization**:
   - URLs were converted to lowercase, trailing slashes were removed, and duplicates were eliminated.

4. **Path Depth Filtering**:
   - URLs with a path depth of 0 (typically homepages) were removed.
   - All URLs with a path depth of 3 or greater were retained.

5. **Word-Boundary Filtering**:
   - URLs with a path depth of less than 3 were retained if they contained popular word-boundary separators such as `-`, `_`, or `.`.
   - For example: `http://kwgs.org/post/funeral-set-ou-quarterback-killed-crash`.


Table 3 presents the number of news articles after filtering.

**Table 3: 3DLNews: Number of news article URLs**

| **Media Type**    | **Google Collected** | **Google Filtered** | **Twitter Collected** | **Twitter Filtered** | **Total Collected** | **Total Filtered** |
|--------------------|-----------------------|-----------------------|------------------------|-----------------------|---------------------|--------------------|
| Newspapers         | 4,992,262            | 2,367,322            | 625,166               | 179,152              | 5,617,428          | 2,509,857         |
| Radio              | 1,069,333            | 202,668              | 119,202               | 8,986                | 1,188,535          | 211,654           |
| TV                 | 888,243              | 523,613              | 63,656                | 13,981               | 951,899            | 537,594           |
| Broadcast          | 837,599              | 470,223              | 74,350                | 16,525               | 911,949            | 486,748           |
| **Total**          | **7,787,437**        | **3,563,826**        | **882,374**           | **218,644**          | **8,669,811**      | **3,782,470**     |


### 3.3 Data Enrichment 

We enhanced the usefulness of the news article URLs in 3DLNews by adding attributes to each URL. Table 4 outlines the complete list of attributes. 

**Table 4: Properties of news article URLs in 3DLNews**

| Property          | Description | Example   |
|-------------------|------------------------|-------------------------|
| link              | The URL of the local news article.| `https://www.adn.com/alaska-news/article/womans-death-montana-has-eerie-echoes-yakutat-killing/2009/01/23/`                  |
| html_filename     | Filename with HTML content of the article.    | `HTML/AK/2009/3e21b4e350560f922993604b9a037793.html.gz`                                     |
| publication_date  | Article publication date.   | `01/23/2009`                                          |
| title             | Title of the article. | `Woman's death in Montana has eerie echoes of Yakutat killing - Anchorage Daily News`  |
| media_name        | Name of local media organization.    | `Alaska Dispatch News`                                       |
| media_type        | Type of media source (*Newspaper* or *TV* or *Radio station* or *Broadcast*). "Broadcast" refers to either TV or radio stations.                           | `newspaper`                                           |
| location          | Location of the media organization. This includes: US state, city, & latitude/longitude.  | <details><summary>location</summary><pre>{"state": "Alaska", "city": "Anchorage", "longitude": -149.87828, "latitude": 61.216799}</pre></details>  |
| media_metadata    | More information about the news media. | <details><summary>media_metadata</summary><pre>{"video": "https://www.youtube.com/user/AlaskaDispatch", "twitter": "http://www.twitter.com/adndotcom", "media-class": "newspaper", "extracted-from": "usnpl.com, thepaperboy.com", "city-county-long": -149.87828, "media-subclass": "city-county", "website": "http://www.adn.com/", "facebook": "https://www.facebook.com/akdispatch", "city-county-lat": 61.216799, "name": "Alaska Dispatch News", "open-search": [], "city-county-name": "Anchorage", "rss": [], "us-state": "Alaska", "wikipedia": "https://en.wikipedia.org/wiki/Anchorage_Daily_News", "instagram": "https://www.instagram.com/alaskadispatch/", "youtube": "https://www.youtube.com/user/AlaskaDispatch"}</pre></details>        |
| source            | Platform (Google or Twitter) where the news article was extracted from.   | `Google`    |
| source_metadata   | More information about the platform scraped.  | <details><summary>source_metadata</summary><pre>{"http://www.adn.com/": {"source": "Google", "query": "news", "extra_params": {"raw_request_params": {"directives": "site:http://www.adn.com/", "search_query_params": "tbs=cdr%3A1%2Ccd_min%3A1%2F1%2F2009%2Ccd_max%3A12%2F31%2F2009", "no_interleave": false, "sleep_sec": 1.5, "files": false, "max_file_depth": 1, "news": false, "find_uri_key": "", "interleave_queries_params": {"count": 1, "news": false, "leave_browser_open": false}, "leave_browser_open": true, "mimic_human_search": false, "chromedriver_path": "", "chromedriver": null, "delay_sec": 0, "html_cache_file": "", "sniff_serp": false}}, "page_details": media_metadata{"result_count": 318, "search_location": {}, "knowledge_panel": {}, "search_state": {"proc_pg_count": 1}, "scraping_report": {"tag": "body", "children": [{"tag": "a", "count": 32, "children": [{"status": "get_title_link() returned empty because: Link has no text (see text: Skip to main content), so likely not SERP link OR href is blank, see href: \"\". Snippet: "}, {"status": "get_title_link() returned empty because: Google native link, see: \"https://support.google.com/websearch/answer/181196?hl=en\". Snippet: "}, {"status": "get_title_link() returned empty because: Link has no text (see text: Accessibility feedback), so likely not SERP link OR href is blank, see href: \"\". Snippet: "}, {"status": "get_title_link() returned empty because: Link has no text (see text: ), so likely not SERP link OR href is blank, see href: \"https://www.google.com/webhp?hl=en&sa=X&ved=0ahUKEwj1_8q27JKEAxUcGFkFHf0HBX0QPAgJ\". Snippet: "}, {"status": "get_title_link() returned empty because: Google native link, see: \"/search?sca_esv=322b65d8a49316d7\". Snippet: "}, {"status": "get_title_link() returned empty because: Link has no text (see text: Try again), so likely not SERP link OR href is blank, see href: \"\". Snippet: "}, {"status": "get_title_link() returned empty because: Link has no text (see text: ), so likely not SERP link OR href is blank, see href: \"\". Snippet: "}], "messages": []}], "count": 0, "misc": {}}, "sniffed_info": {}, "related_questions": [], "related_queries": [], "captcha_on": false}, "self_uris": [{"page": 1, "uri": "https://www.google.com/search?tbs=cdr%3A1%2Ccd_min%3A1%2F1%2F2009%2Ccd_max%3A12%2F31%2F2009&q=news%20site:http://www.adn.com/"}], "max_page": 1, "gen_timestamp": "2024-02-04T23:33:47Z", "links": [{"link": "http://www.adn.com/", "title": "here", "date": "Feb 04, 2024", "snippet": "", "rank": 0, "page": 1, "custom": {"link_class": "main_blue_link", "date_auto_gen": false, "children": []}}, {"link": "#", "title": "Turn off continuous scrolling", "date": "Feb 04, 2024", "snippet": "", "rank": 1, "page": 1, "custom": {"link_class": "main_blue_link", "date_auto_gen": false, "children": []}}, {"link": "https://www.adn.com/author/bradford-h-tuck", "title": "Bradford Tuckadn.comhttps://www.adn.com \u203a author \u203a bradford-h-tuck", "date": "Feb 04, 2024", "snippet": "", "rank": 2, "page": 1, "custom": {"link_class": "main_blue_link", "date_auto_gen": false, "children": []}}, {"link": "https://www.adn.com/author/paulette-simpson/", "title": "Paulette_Simpsonadn.comhttps://www.adn.com \u203a author \u203a paulette-simpson", "date": "Feb 04, 2024", "snippet": "", "rank": 3, "page": 1, "custom": {"link_class": "main_blue_link", "date_auto_gen": false, "children": []}}, {"link": "https://www.adn.com/features/article/fourth-kind-pays-telling-big-fib/2009/11/12/", "title": "'The Fourth Kind' pays for telling a big fibadn.comhttps://www.adn.com \u203a features \u203a article \u203a 2009/11/12", "date": "Feb 04, 2024", "snippet": "", "rank": 4, "page": 1, "custom": {"link_class": "main_blue_link", "date_auto_gen": false, "children": []}}, {"link": "https://www.adn.com/alaska-news/article/two-persons-found-dead-recently-are-identified/2009/08/11/", "title": "Two persons found dead recently are identifiedadn.comhttps://www.adn.com \u203a alaska-news \u203a article \u203a 2009/08/11", "date": "Feb 04, 2024", "snippet": "", "rank": 5, "page": 1, "custom": {"link_class": "main_blue_link", "date_auto_gen": false, "children": []}}, {"link": "https://www.adn.com/alaska-news/article/allan-tesche-dead-60-remembered-political-fighter/2009/07/14/", "title": "Allan Tesche, dead at 60, remembered as political fighteradn.comhttps://www.adn.com \u203a alaska-news \u203a article \u203a 2009/07/14", "date": "Feb 04, 2024", "snippet": "", "rank": 6, "page": 1, "custom": {"link_class": "main_blue_link", "date_auto_gen": false, "children": []}}, {"link": "https://www.adn.com/alaska-news/article/police-captain-retires-shortly-after-accident/2009/04/04/", "title": "Police captain retires shortly after accidentadn.comhttps://www.adn.com \u203a alaska-news \u203a article \u203a 2009/04/04", "date": "Feb 04, 2024", "snippet": "", "rank": 7, "page": 1, "custom": {"link_class": "main_blue_link", "date_auto_gen": false, "children": []}}, {"link": "https://www.adn.com/economy/article/longtime-ktuu-newsman-loses-job/2009/02/03/", "title": "Longtime KTUU newsman loses jobadn.comhttps://www.adn.com \u203a economy \u203a article \u203a 2009/02/03", "date": "Feb 04, 2024", "snippet": "", "rank": 8, "page": 1, "custom": {"link_class": "main_blue_link", "date_auto_gen": false, "children": []}}, {"link": "https://www.adn.com/alaska-news/article/feds-charge-4-sex-traffic-kids-involved/2009/12/18/", "title": "Feds charge 4 for sex traffic; kids involvedadn.comhttps://www.adn.com \u203a alaska-news \u203a article \u203a 2009/12/18", "date": "Feb 04, 2024", "snippet": "", "rank": 9, "page": 1, "custom": {"link_class": "main_blue_link", "date_auto_gen": false, "children": []}}, {"link": "https://www.adn.com/alaska-news/article/body-found-matanuska-river-believed-palmer-teens/2009/08/27/", "title": "Body found in Matanuska River believed Palmer teen'sadn.comhttps://www.adn.com \u203a alaska-news \u203a article \u203a 2009/08/27", "date": "Feb 04, 2024", "snippet": "", "rank": 10, "page": 1, "custom": {"link_class": "main_blue_link", "date_auto_gen": false, "children": []}}, {"link": "https://www.adn.com/alaska-news/article/womans-death-montana-has-eerie-echoes-yakutat-killing/2009/01/23/", "title": "Woman's death in Montana has eerie echoes of Yakutat ...adn.comhttps://www.adn.com \u203a alaska-news \u203a article \u203a 2009/01/23", "date": "Feb 04, 2024", "snippet": "", "rank": 11, "page": 1, "custom": {"link_class": "main_blue_link", "date_auto_gen": false, "children": []}}], "stats": {"total_links": 12, "domain_dist": {"top_k_domain_link_count": 11, "col_frac": 0.9166666666666666, "top_k_domains": [["adn.com", 11]], "k": 0}}}}</pre></details>                              |
| response_code     | Response code returned following GET request of link.                                                                                                      | `200`                                                 |
| expanded_url      | Final target URL for links that redirect.                                                                                                                  | `None`          |
| is_news_article      |  Indicates whether the link is filtered as a news article based on our filtering process.                                                                                                                | true        |

### 3.4 Data Format

- The structure of the dataset is as follows.
  ```
  ├── Google
  │   ├── 1-Newspapers
  │   │   ├── state
  │   │   │   ├── AK
  │   |   │   |   ├── google_newspaper_AK_2006.jsonl.gz
  │   |   │   |   ├── google_newspaper_AK_2007.jsonl.gz
  │   |   │   |   ├── -------------------------------
  │   │   │   ├── --
  │   │   │   └── WY
  │   |   │       ├── google_newspaper_AK_2006.jsonl.gz
  │   |   │       ├── google_newspaper_AK_2007.jsonl.gz
  │   |   │       ├── -------------------------------
  │   │   ├── preprocessed_stat
  │   │   │   ├── AK
  │   |   │   |   ├── preprocessed_google_newspaper_AK_2006.jsonl.gz
  │   |   │   |   ├── preprocessed_google_newspaper_AK_2007.jsonl.gz
  │   |   │   |   ├── -------------------------------
  │   │   │   ├── --
  │   │   │   └── WY
  │   |   │       ├── preprocessed_google_newspaper_AK_2006.jsonl.gz
  │   |   │       ├── preprocessed_google_newspaper_AK_2007.jsonl.gz
  │   |   │       ├── -------------------------------
  │   │   ├── HTML
  │   │   │   ├── AK
  │   │   │   │   ├── 1996
  │   │   │   │   │   ├── 0106eb41fcb93351d3bba81a67ecf487.html.gz
  │   │   │   │   │   ├── 024b602f2a0c7edf53ee2a1b0228bfc5.html.gz
  │   │   │   │   │   ├── -------------------------------------  
  │   │   │   │   ├── ----
  │   │   │   │   └──2024
  │   │   │   │       ├── 0106eb41fcb93351d3bba81a67ecf487.html.gz
  │   │   │   │       ├── 024b602f2a0c7edf53ee2a1b0228bfc5.html.gz
  │   │   │   │       ├── -------------------------------------  
  │   ├── 2-Radio
  │   ├── 3-TV
  │   └── 4-Broadcast
  └── Twitter
      ├── 1-Newspapers
      ├── 2-Radio
      ├── 3-TV
      └── 4-Broadcast
  ```
The Google directory contains JSONL files with news article URLs extracted through Google scraping. Each JSONL file represents a collection of URLs and their associated metadata gathered from automated searches on Google.

The Twitter directory holds JSONL files with news article URLs obtained via Twitter scraping. Each JSONL file includes URLs and metadata collected from tweets, providing a diverse set of news articles shared on the Twitter platform.

Within both the Twitter and Google directories, there are three main directories for each news media type. Inside each media type folder, the following main directories are included:

- **state:** Contains scraped data for each state for each year.
- **preprocessed_data:** Contains directories for each state. Within each state directory, there are jsonl.gz files for each year, which include data objects for each URL with metadata.
- **HTML:** Contains the HTML content for each article for each state for each year, named with the hash value of each article URL.

  
### 4. Potential Applications of 3DLNews Dataset
- Exploring the Nationalization of Local News
- Media Bias Analysis
- Studying US Local News Deserts
- Community Understanding, Trend Analysis and Prediction
