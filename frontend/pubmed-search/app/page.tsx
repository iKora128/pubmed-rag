import { AdvancedSearchForm } from '@/components/search/advanced-search-form'

export default function Home() {
  return (
    <div className="container mx-auto px-4 py-16">
      <h1 className="text-4xl font-bold text-center mb-6">PubMed Advanced Search</h1>
      <p className="text-lg text-center text-muted-foreground mb-8">
        Search through millions of medical research articles with advanced filters
      </p>
      <AdvancedSearchForm />
    </div>
  )
}