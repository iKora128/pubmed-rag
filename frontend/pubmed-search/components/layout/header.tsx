'use client'

import Link from 'next/link'
import { useAuth } from '@/components/auth/use-auth'
import { Button } from "@/components/ui/button"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { MainNav } from './main-nav'
import { useState } from 'react'
import { LoginModal } from '@/components/auth/login-modal'
import { SignupModal } from '@/components/auth/signup-modal'
import { getFirebaseAuth } from '@/lib/firebase/config'

export function Header() {
  const { user } = useAuth()
  const auth = getFirebaseAuth()
  const [isLoginModalOpen, setLoginModalOpen] = useState(false)
  const [isSignupModalOpen, setSignupModalOpen] = useState(false)

  const handleSignOut = () => {
    auth.signOut()
  }

  return (
    <header className="border-b">
      <div className="container mx-auto px-4 h-16 flex items-center justify-between">
        <div className="flex items-center gap-6">
          <Link href="/" className="font-semibold text-lg">
            PubMed Search
          </Link>
          {user && <MainNav />}
        </div>

        <div className="flex items-center gap-4">
          {user ? (
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button variant="ghost" className="relative h-8 w-8 rounded-full">
                  <Avatar className="h-8 w-8">
                    <AvatarImage src={user.photoURL || ''} alt={user.email || ''} />
                    <AvatarFallback>{user.email?.[0].toUpperCase()}</AvatarFallback>
                  </Avatar>
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent className="w-56" align="end" forceMount>
                <DropdownMenuLabel className="font-normal">
                  <div className="flex flex-col space-y-1">
                    <p className="text-sm font-medium leading-none">{user.email}</p>
                  </div>
                </DropdownMenuLabel>
                <DropdownMenuSeparator />
                <DropdownMenuItem asChild>
                  <Link href="/profile">Profile</Link>
                </DropdownMenuItem>
                <DropdownMenuItem asChild>
                  <Link href="/settings">Settings</Link>
                </DropdownMenuItem>
                <DropdownMenuSeparator />
                <DropdownMenuItem onClick={handleSignOut}>
                  Log out
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          ) : (
            <>
              <Button variant="ghost" onClick={() => setLoginModalOpen(true)}>
                Log In
              </Button>
              <Button variant="ghost" onClick={() => setSignupModalOpen(true)}>
                Sign Up
              </Button>
            </>
          )}
        </div>
      </div>
      <LoginModal isOpen={isLoginModalOpen} onClose={() => setLoginModalOpen(false)} />
      <SignupModal isOpen={isSignupModalOpen} onClose={() => setSignupModalOpen(false)} />
    </header>
  )
}