'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import { onAuthStateChanged, sendEmailVerification, User } from 'firebase/auth'
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { getFirebaseAuth } from '@/lib/firebase/config'

export default function VerifyEmailPage() {
  const router = useRouter()
  const [user, setUser] = useState<User | null>(null)
  const [isLoading, setIsLoading] = useState(false)

  useEffect(() => {
    const auth = getFirebaseAuth()
    const unsubscribe = onAuthStateChanged(auth, (currentUser) => {
      if (currentUser) {
        setUser(currentUser)
        if (currentUser.emailVerified) {
          router.push('/')
        }
      } else {
        router.push('/auth/login')
      }
    })

    return () => unsubscribe()
  }, [router])

  const handleResendEmail = async () => {
    if (user && !user.emailVerified) {
      setIsLoading(true)
      try {
        await sendEmailVerification(user)
        alert('Verification email sent. Please check your inbox.')
      } catch (error) {
        console.error('Error sending verification email:', error)
        alert('Failed to send verification email. Please try again.')
      } finally {
        setIsLoading(false)
      }
    }
  }

  return (
    <div className="container mx-auto flex items-center justify-center min-h-screen px-4">
      <Card className="w-full max-w-md">
        <CardHeader>
          <CardTitle className="text-2xl font-bold text-center">Verify Your Email</CardTitle>
          <CardDescription className="text-center">
            We've sent a verification email to your address. Please check your inbox and click the verification link.
          </CardDescription>
        </CardHeader>
        <CardContent className="flex flex-col items-center">
          <p className="mb-4 text-center">
            If you don't see the email, check your spam folder or click the button below to resend the verification email.
          </p>
          <Button onClick={handleResendEmail} disabled={isLoading}>
            {isLoading ? 'Sending...' : 'Resend Verification Email'}
          </Button>
        </CardContent>
      </Card>
    </div>
  )
}