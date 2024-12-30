'use client'

import { ArticleResponse } from '@/types'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Checkbox } from '@/components/ui/checkbox'

interface SearchResultsProps {
  results: ArticleResponse[]
  selectedArticles: ArticleResponse[]
  onArticleSelect: (article: ArticleResponse) => void
}

export function SearchResults({ results, selectedArticles, onArticleSelect }: SearchResultsProps) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>検索結果（{results.length}件）</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {results.map(article => (
            <div key={article.pmid} className="flex items-start space-x-3 p-3 hover:bg-gray-50 rounded-lg">
              <Checkbox
                checked={selectedArticles.some(a => a.pmid === article.pmid)}
                onCheckedChange={() => onArticleSelect(article)}
              />
              <div>
                <h3 className="font-medium text-sm">{article.title}</h3>
                <p className="text-xs text-gray-600 mt-1">
                  {article.authors.map(a => `${a.last_name} ${a.fore_name}`).join(', ')}
                </p>
                <p className="text-xs text-gray-500 mt-1">
                  {article.journal} ({article.publication_date.year})
                </p>
              </div>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  )
}

