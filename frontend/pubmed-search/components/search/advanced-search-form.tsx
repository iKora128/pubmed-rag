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
import { SearchRequest } from '@/types'
import { useAuth } from '@/components/auth/use-auth'

export function AdvancedSearchForm() {
  const [searchRequest, setSearchRequest] = useState<SearchRequest>({
    query: '',
    journal: '',
    author: '',
    dateRange: '',
    evidenceLevel: undefined,
  })
  const router = useRouter()
  const { user } = useAuth()

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!user) {
      router.push('/auth/login')
      return
    }

    const queryParams = new URLSearchParams()
    Object.entries(searchRequest).forEach(([key, value]) => {
      if (value) {
        queryParams.append(key, value)
      }
    })

    router.push(`/search?${queryParams.toString()}`)
  }

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target
    setSearchRequest(prev => ({ ...prev, [name]: value }))
  }

  const handleSelectChange = (name: string, value: string) => {
    setSearchRequest(prev => ({ ...prev, [name]: value }))
  }

  return (
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
          <Button type="submit" className="w-full">
            Search
          </Button>
        </form>
      </CardContent>
    </Card>
  )
}