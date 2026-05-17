import requests

def search_pubmed(query: str) -> str:
    """
    Search the NCBI PubMed database for medical research articles.
    """
    try:
        search_url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term={query}&retmode=json&retmax=3"
        search_res = requests.get(search_url, timeout=10).json()
        
        article_ids = search_res.get("esearchresult", {}).get("idlist", [])
        if not article_ids:
            return f"No PubMed articles found for query: '{query}'."
            
        ids_str = ",".join(article_ids)
        summary_url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=pubmed&id={ids_str}&retmode=json"
        summary_res = requests.get(summary_url, timeout=10).json()
        
        results = summary_res.get("result", {})
        
        output = f"**PubMed Research Articles for '{query}':**\n"
        for uid in article_ids:
            article = results.get(uid, {})
            title = article.get("title", "No Title")
            source = article.get("source", "Unknown Source")
            pubdate = article.get("pubdate", "")
            
            output += f"- **{title}** (*{source}*, {pubdate})\n"
            output += f"  Link: https://pubmed.ncbi.nlm.nih.gov/{uid}/\n\n"
            
        return output
        
    except Exception as e:
        return f"Error querying PubMed: {str(e)}"
