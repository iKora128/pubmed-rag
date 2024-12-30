'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card'
import { Label } from '@/components/ui/label'
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from '@/components/ui/tooltip'
import { Info } from 'lucide-react'
import { SearchRequest, ArticleResponse } from '@/types'
import { useAuth } from '@/components/auth/use-auth'
import { Checkbox } from '@/components/ui/checkbox'
import { ArticleGenerator } from '@/components/article/article-generator'

export function AdvancedSearchForm({ onSearch }: { onSearch: (searchRequest: SearchRequest) => Promise<ArticleResponse[]> }) {
  const [searchRequest, setSearchRequest] = useState<SearchRequest>({
    query: '',
    journal: '',
    author: '',
    dateRange: '',
    evidenceLevel: undefined,
    publicationTypes: [],
    meshTerms: [],
    startYear: undefined,
    endYear: undefined,
    languages: [],
    freeFullText: false,
    humansOnly: false,
    maxResults: 100,
    sortBy: 'relevance',
  })
  const router = useRouter()
  const { user } = useAuth()
  const [selectedArticles, setSelectedArticles] = useState<ArticleResponse[]>([])
  const [searchResults, setSearchResults] = useState<ArticleResponse[]>([])

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!user) {
      router.push('/auth/login')
      return
    }

    try {
      const results = await onSearch(searchRequest)
      setSearchResults(results)
    } catch (error) {
      console.error('Search failed:', error)
    }
  }

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target
    setSearchRequest(prev => ({ ...prev, [name]: value }))
  }

  const handleSelectChange = (name: string, value: string | string[]) => {
    setSearchRequest(prev => ({ ...prev, [name]: value }))
  }

  const handleCheckboxChange = (name: string, checked: boolean) => {
    setSearchRequest(prev => ({ ...prev, [name]: checked }))
  }

  const handleArticleSelect = (article: ArticleResponse) => {
    setSelectedArticles(prev => {
      const exists = prev.some(a => a.pmid === article.pmid)
      if (exists) {
        return prev.filter(a => a.pmid !== article.pmid)
      }
      return [...prev, article]
    })
  }

  return (
    <div className="space-y-6">
      <Card className="w-full max-w-2xl mx-auto">
        <CardHeader>
          <CardTitle>Advanced Search</CardTitle>
          <CardDescription>Refine your search with advanced options</CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSearch} className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="query">Search Query</Label>
                <Input
                  id="query"
                  name="query"
                  value={searchRequest.query}
                  onChange={handleInputChange}
                  placeholder="Enter your search terms"
                  required
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="journal">Journal</Label>
                <Input
                  id="journal"
                  name="journal"
                  value={searchRequest.journal}
                  onChange={handleInputChange}
                  placeholder="Enter journal name"
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="author">Author</Label>
                <Input
                  id="author"
                  name="author"
                  value={searchRequest.author}
                  onChange={handleInputChange}
                  placeholder="Enter author name"
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="dateRange">Date Range</Label>
                <Select
                  name="dateRange"
                  value={searchRequest.dateRange}
                  onValueChange={(value) => handleSelectChange('dateRange', value)}
                >
                  <SelectTrigger id="dateRange">
                    <SelectValue placeholder="Select date range" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="1 Year">Last 1 Year</SelectItem>
                    <SelectItem value="5 Years">Last 5 Years</SelectItem>
                    <SelectItem value="10 Years">Last 10 Years</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <div className="space-y-2">
                <Label htmlFor="startYear">Start Year</Label>
                <Input
                  id="startYear"
                  name="startYear"
                  type="number"
                  value={searchRequest.startYear || ''}
                  onChange={handleInputChange}
                  placeholder="Enter start year"
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="endYear">End Year</Label>
                <Input
                  id="endYear"
                  name="endYear"
                  type="number"
                  value={searchRequest.endYear || ''}
                  onChange={handleInputChange}
                  placeholder="Enter end year"
                />
              </div>
            </div>
            <div className="space-y-2">
              <div className="flex items-center space-x-2">
                <Label htmlFor="evidenceLevel">Evidence Level</Label>
                <TooltipProvider>
                  <Tooltip>
                    <TooltipTrigger>
                      <Info className="h-4 w-4 text-muted-foreground" />
                    </TooltipTrigger>
                    <TooltipContent>
                      <p>Evidence levels are based on study design and methodology:</p>
                      <ul className="list-disc list-inside">
                        <li>High: RCTs, Systematic Reviews, Meta-Analyses</li>
                        <li>Medium: Clinical Trials, Comparative Studies</li>
                        <li>Low: Case Reports, Observational Studies</li>
                      </ul>
                    </TooltipContent>
                  </Tooltip>
                </TooltipProvider>
              </div>
              <Select
                name="evidenceLevel"
                value={searchRequest.evidenceLevel}
                onValueChange={(value) => handleSelectChange('evidenceLevel', value)}
              >
                <SelectTrigger id="evidenceLevel">
                  <SelectValue placeholder="Select evidence level" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="high">High (RCTs, Systematic Reviews, Meta-Analyses)</SelectItem>
                  <SelectItem value="medium">Medium (Clinical Trials, Comparative Studies)</SelectItem>
                  <SelectItem value="low">Low (Case Reports, Observational Studies)</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div className="space-y-2">
              <Label>Publication Types</Label>
              <div className="space-y-2">
                {["Meta-Analysis", "Systematic Review", "Randomized Controlled Trial", "Clinical Trial", "Review"].map((type) => (
                  <div key={type} className="flex items-center space-x-2">
                    <Checkbox
                      id={`publicationType-${type}`}
                      checked={searchRequest.publicationTypes.includes(type)}
                      onCheckedChange={(checked) => {
                        if (checked) {
                          handleSelectChange('publicationTypes', [...searchRequest.publicationTypes, type])
                        } else {
                          handleSelectChange('publicationTypes', searchRequest.publicationTypes.filter(t => t !== type))
                        }
                      }}
                    />
                    <Label htmlFor={`publicationType-${type}`}>{type}</Label>
                  </div>
                ))}
              </div>
            </div>
            <div className="space-y-2">
              <Label>Languages</Label>
              <div className="space-y-2">
                {["english", "japanese", "french", "german", "chinese", "spanish"].map((lang) => (
                  <div key={lang} className="flex items-center space-x-2">
                    <Checkbox
                      id={`language-${lang}`}
                      checked={searchRequest.languages.includes(lang)}
                      onCheckedChange={(checked) => {
                        if (checked) {
                          handleSelectChange('languages', [...searchRequest.languages, lang])
                        } else {
                          handleSelectChange('languages', searchRequest.languages.filter(l => l !== lang))
                        }
                      }}
                    />
                    <Label htmlFor={`language-${lang}`}>{lang.charAt(0).toUpperCase() + lang.slice(1)}</Label>
                  </div>
                ))}
              </div>
            </div>
            <div className="flex items-center space-x-2">
              <Checkbox
                id="freeFullText"
                checked={searchRequest.freeFullText}
                onCheckedChange={(checked) => handleCheckboxChange('freeFullText', checked as boolean)}
              />
              <Label htmlFor="freeFullText">Free Full Text</Label>
            </div>
            <div className="flex items-center space-x-2">
              <Checkbox
                id="humansOnly"
                checked={searchRequest.humansOnly}
                onCheckedChange={(checked) => handleCheckboxChange('humansOnly', checked as boolean)}
              />
              <Label htmlFor="humansOnly">Humans Only</Label>
            </div>
            <div className="space-y-2">
              <Label htmlFor="maxResults">Max Results</Label>
              <Input
                id="maxResults"
                name="maxResults"
                type="number"
                value={searchRequest.maxResults}
                onChange={handleInputChange}
                min={1}
                max={10000}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="sortBy">Sort By</Label>
              <Select
                name="sortBy"
                value={searchRequest.sortBy}
                onValueChange={(value) => handleSelectChange('sortBy', value)}
              >
                <SelectTrigger id="sortBy">
                  <SelectValue placeholder="Select sort order" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="relevance">Relevance</SelectItem>
                  <SelectItem value="date">Date</SelectItem>
                  <SelectItem value="journal">Journal</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <Button type="submit" className="w-full">
              Search
            </Button>
          </form>
        </CardContent>
      </Card>

      {searchResults.length > 0 && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <Card>
            <CardHeader>
              <CardTitle>検索結果</CardTitle>
            </CardHeader>
            <CardContent>
              {searchResults.map(article => (
                <div key={article.pmid} className="flex items-start space-x-2 mb-4">
                  <Checkbox
                    checked={selectedArticles.some(a => a.pmid === article.pmid)}
                    onCheckedChange={() => handleArticleSelect(article)}
                  />
                  <div>
                    <h3 className="font-medium">{article.title}</h3>
                    <p className="text-sm text-gray-600">
                      {article.authors.map(a => `${a.last_name} ${a.fore_name}`).join(', ')}
                    </p>
                  </div>
                </div>
              ))}
            </CardContent>
          </Card>

          <ArticleGenerator selectedArticles={selectedArticles} />
        </div>
      )}
    </div>
  )
}