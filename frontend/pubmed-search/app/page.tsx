'use client'

import { useState } from 'react'
import { AdvancedSearchForm } from '@/components/search/advanced-search-form'
import { SearchResults } from '@/components/search/search-results'
import { ArticleResponse, SearchRequest } from '@/types'

export default function Home() {
  const [searchResults, setSearchResults] = useState<ArticleResponse[]>([])
  const [isLoading, setIsLoading] = useState(false)

  const handleSearch = async (searchRequest: SearchRequest) => {
    setIsLoading(true)
    try {
      // Replace this with your actual API call to the backend
      const response = await fetch('/api/pubmed-search', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(searchRequest),
      })
      const data = await response.json()
      setSearchResults(data)
    } catch (error) {
      console.error('Error fetching search results:', error)
      // Handle error (e.g., show error message to user)
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="container mx-auto px-4 py-16">
      <h1 className="text-4xl font-bold text-center mb-6">PubMed Advanced Search</h1>
      <p className="text-lg text-center text-muted-foreground mb-8">
        Search through millions of medical research articles with advanced filters
      </p>
      <AdvancedSearchForm onSearch={handleSearch} />
      {isLoading && <p className="text-center mt-8">Loading results...</p>}
      {!isLoading && searchResults.length > 0 && (
        <div className="mt-8">
          <h2 className="text-2xl font-semibold mb-4">Search Results</h2>
          <SearchResults results={searchResults} />
        </div>
      )}
    </div>
  )
}

