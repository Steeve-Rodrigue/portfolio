"use client"

import { useEffect, useState } from "react"
import UserList from "@/components/UserList"

type User = {
  id: number
  name: string
}

export default function UsersPage() {
  const [users, setUsers] = useState<User[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const fetchUsers = async () => {
      try {
        const res = await fetch("http://localhost:8000/users")
        if (!res.ok) throw new Error("Error fetching users")

        const data = await res.json()
        setUsers(data)
      } catch (err: any) {
        setError(err.message)
      } finally {
        setLoading(false)
      }
    }

    fetchUsers()
  }, [])

  return (
    <div className="min-h-screen bg-gray-50 py-10 px-4">
      <div className="max-w-6xl mx-auto">
        
        {/* Header */}
        <div className="mb-8 text-center">
          <h1 className="text-3xl font-bold text-gray-800">
            Users Dashboard
          </h1>
          <p className="text-gray-500 mt-2">
            List of all registered users
          </p>
        </div>

        {/* States */}
        {loading && (
          <p className="text-center text-gray-500">
            Loading users...
          </p>
        )}

        {error && (
          <p className="text-center text-red-500">
            {error}
          </p>
        )}

        {!loading && !error && <UserList users={users} />}
      </div>
    </div>
  )
}