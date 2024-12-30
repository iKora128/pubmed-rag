import { http, HttpResponse } from 'msw'
import { ArticleResponse } from '@/types'

interface GenerateArticleRequest {
  search_results: ArticleResponse[]
}

export const handlers = [
  http.post('/api/pubmed-search', async ({ request }) => {
    const searchData = await request.json()
    
    // モックレスポンスを返す
    return HttpResponse.json([
      {
        pmid: "12345678",
        title: "Test Article",
        abstract: "This is a test abstract.",
        authors: [
          {
            fore_name: "John",
            last_name: "Smith"
          }
        ],
        journal: "Test Journal",
        publication_date: {
          year: 2024,
          month: 1,
          day: 1
        },
        mesh_terms: [
          {
            descriptor: "Test Term"
          }
        ],
        url: "https://pubmed.ncbi.nlm.nih.gov/12345678"
      }
    ])
  }),

  http.post('/api/generate-article', async ({ request }) => {
    const { search_results } = await request.json() as GenerateArticleRequest
    
    return HttpResponse.json({
      id: 1,
      title: "Generated Article",
      content: "# Literature Review\n\nTest content",
      summary: "Test summary",
      keywords: ["test"],
      source_articles: [search_results[0].pmid],
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString()
    })
  })
] 