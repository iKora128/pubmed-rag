'use client'

import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { ArticleResponse } from '@/types'
import { Loader2 } from "lucide-react"

interface ArticleGeneratorProps {
  selectedArticles: ArticleResponse[]
}

export function ArticleGenerator({ selectedArticles }: ArticleGeneratorProps) {
  const [isGenerating, setIsGenerating] = useState(false)
  const [generatedArticle, setGeneratedArticle] = useState<any>(null)

  const handleGenerate = async () => {
    setIsGenerating(true)
    try {
      const response = await fetch('/api/generate-article', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(selectedArticles),
      })
      
      if (!response.ok) throw new Error('記事の生成に失敗しました')
      
      const article = await response.json()
      setGeneratedArticle(article)
    } catch (error) {
      console.error('Error:', error)
      // エラー処理
    } finally {
      setIsGenerating(false)
    }
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>記事生成</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          <div>
            選択された論文: {selectedArticles.length}件
          </div>
          <Button 
            onClick={handleGenerate}
            disabled={isGenerating || selectedArticles.length === 0}
          >
            {isGenerating ? <Loader2 className="h-4 w-4 animate-spin" /> : '記事を生成'}
          </Button>
          
          {generatedArticle && (
            <div className="mt-4 space-y-4">
              <h2 className="text-xl font-bold">{generatedArticle.title}</h2>
              <div className="prose max-w-none">
                {generatedArticle.content}
              </div>
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  )
} 