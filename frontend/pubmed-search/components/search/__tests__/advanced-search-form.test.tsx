import { render, screen, fireEvent } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { AdvancedSearchForm } from '../advanced-search-form'

describe('AdvancedSearchForm', () => {
  const mockOnSearch = jest.fn()

  beforeEach(() => {
    mockOnSearch.mockClear()
  })

  it('基本的な検索フォームの要素が表示される', () => {
    render(<AdvancedSearchForm onSearch={mockOnSearch} />)
    
    // 基本的な入力フィールドの存在確認
    expect(screen.getByPlaceholderText(/キーワードを入力/i)).toBeInTheDocument()
    expect(screen.getByLabelText(/ジャーナル/i)).toBeInTheDocument()
    expect(screen.getByLabelText(/著者/i)).toBeInTheDocument()
  })

  it('検索ボタンをクリックすると検索が実行される', async () => {
    render(<AdvancedSearchForm onSearch={mockOnSearch} />)
    
    // キーワードを入力
    const keywordInput = screen.getByPlaceholderText(/キーワードを入力/i)
    await userEvent.type(keywordInput, 'COVID-19')
    
    // 検索ボタンをクリック
    const searchButton = screen.getByRole('button', { name: /検索/i })
    await userEvent.click(searchButton)
    
    // onSearch関数が正しいパラメータで呼ばれることを確認
    expect(mockOnSearch).toHaveBeenCalledWith(
      expect.objectContaining({
        query: 'COVID-19',
        maxResults: expect.any(Number)
      })
    )
  })

  it('フィルターオプションが正しく機能する', async () => {
    render(<AdvancedSearchForm onSearch={mockOnSearch} />)
    
    // 出版タイプを選択
    const metaAnalysisCheckbox = screen.getByLabelText(/メタアナリシス/i)
    await userEvent.click(metaAnalysisCheckbox)
    
    // 言語を選択
    const englishCheckbox = screen.getByLabelText(/英語/i)
    await userEvent.click(englishCheckbox)
    
    // 検索を実行
    const searchButton = screen.getByRole('button', { name: /検索/i })
    await userEvent.click(searchButton)
    
    // フィルターが含まれていることを確認
    expect(mockOnSearch).toHaveBeenCalledWith(
      expect.objectContaining({
        publicationTypes: expect.arrayContaining(['Meta-Analysis']),
        languages: expect.arrayContaining(['en'])
      })
    )
  })
}) 