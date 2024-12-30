import { render, screen } from '@testing-library/react'
import { SearchResults } from '../search-results'
import { ArticleResponse } from '@/types'

describe('SearchResults', () => {
  const mockResults: ArticleResponse[] = [
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
        year: "2024"
      },
      mesh_terms: [
        {
          descriptor: "Test Term"
        }
      ],
      url: "https://pubmed.ncbi.nlm.nih.gov/12345678"
    }
  ]
  const mockSelectedArticles: ArticleResponse[] = []
  const mockOnArticleSelect = jest.fn()

  it('検索結果が正しく表示される', () => {
    render(
      <SearchResults
        results={mockResults}
        selectedArticles={mockSelectedArticles}
        onArticleSelect={mockOnArticleSelect}
      />
    )
    
    // タイトルが表示される
    expect(screen.getByText('Test Article')).toBeInTheDocument()
    
    // 著者が表示される
    expect(screen.getByText(/John Smith/)).toBeInTheDocument()
    
    // ジャーナル情報が表示される
    expect(screen.getByText(/Test Journal/)).toBeInTheDocument()
    
    // 出版年が表示される
    expect(screen.getByText(/2024/)).toBeInTheDocument()
  })

  it('検索結果が空の場合、適切なメッセージが表示される', () => {
    render(
      <SearchResults
        results={[]}
        selectedArticles={mockSelectedArticles}
        onArticleSelect={mockOnArticleSelect}
      />
    )
    expect(screen.getByText(/検索結果がありません/i)).toBeInTheDocument()
  })

  it('PubMedリンクが正しく機能する', () => {
    render(
      <SearchResults
        results={mockResults}
        selectedArticles={mockSelectedArticles}
        onArticleSelect={mockOnArticleSelect}
      />
    )
    const link = screen.getByRole('link', { name: /pubmedで見る/i })
    expect(link).toHaveAttribute('href', 'https://pubmed.ncbi.nlm.nih.gov/12345678')
    expect(link).toHaveAttribute('target', '_blank')
  })
}) 