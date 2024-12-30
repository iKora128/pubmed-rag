export interface SearchRequest {
    query: string
    journal: string
    author: string
    dateRange: string
    evidenceLevel?: string
    publicationTypes: string[]
    meshTerms: string[]
    startYear?: number
    endYear?: number
    languages: string[]
    freeFullText: boolean
    humansOnly: boolean
    maxResults: number
    sortBy: string
}

export interface ArticleResponse {
  pmid: string
  title: string
  authors: {
    fore_name: string
    last_name: string
  }[]
  journal: string
  publication_date: {
    year: string
  }
  abstract: string
  mesh_terms: {
    descriptor: string
  }[]
  url: string
}