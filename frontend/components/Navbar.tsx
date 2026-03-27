import Link from "next/link"

export default function Navbar() {
  return (
    <nav className="bg-white shadow-md px-6 py-4 flex justify-between items-center">
      <h1 className="text-lg md:text-xl font-bold">My Portfolio</h1>

      <div className="space-x-4">
        <Link href="/">
          <span className="cursor-pointer hover:text-blue-600">Home</span>
        </Link>
        <Link href="/users">
          <span className="cursor-pointer hover:text-blue-600">Users</span>
        </Link>
      </div>
    </nav>
  )
}