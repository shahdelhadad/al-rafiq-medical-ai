import requests

def search_openfda_drug_reactions(drug_name: str) -> str:
    """
    Query the OpenFDA API for the most common adverse reactions reported for a specific drug.
    """
    try:
        url = f'https://api.fda.gov/drug/event.json?search=patient.drug.medicinalproduct:"{drug_name}"&count=patient.reaction.reactionmeddrapt.exact'
        response = requests.get(url, timeout=10)
        
        if response.status_code != 200:
            return f"Could not find FDA data for drug '{drug_name}'."
            
        data = response.json()
        results = data.get("results", [])
        
        if not results:
            return f"No adverse reaction data found in OpenFDA for '{drug_name}'."
            
        # Extract the top 5 adverse reactions
        top_reactions = results[:5]
        
        output = f"**OpenFDA Adverse Reactions for {drug_name.capitalize()}:**\n"
        for rxn in top_reactions:
            output += f"- {rxn['term']} ({rxn['count']} reported cases)\n"
            
        return output
        
    except Exception as e:
        return f"Error querying OpenFDA: {str(e)}"
