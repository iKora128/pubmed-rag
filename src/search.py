from scheme import SearchRequest

def construct_search_query(request: SearchRequest) -> str:
    query = request.query
    if request.journal:
        query += f" AND {request.journal}[journal]"
    if request.author:
        query += f" AND {request.author}[author]"
    if request.date_range:
        query += f" AND {request.date_range}[pdat]"
    if request.evidence_level:
        # エビデンスレベルに基づいてクエリを調整
        if request.evidence_level == "high":
            query += " AND (\"Randomized Controlled Trial\"[Publication Type] OR \"Systematic Review\"[Publication Type] OR \"Meta-Analysis\"[Publication Type])"
        elif request.evidence_level == "medium":
            query += " AND (\"Clinical Trial\"[Publication Type] OR \"Comparative Study\"[Publication Type])"
        elif request.evidence_level == "low":
            query += " AND (\"Case Reports\"[Publication Type] OR \"Observational Study\"[Publication Type])"
    return query