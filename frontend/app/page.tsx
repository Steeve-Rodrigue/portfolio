import Link from "next/link"

export default function Home() {
  return (
    <div className="min-h-screen flex flex-col items-center justify-center text-center px-4">
      <h1 className="text-2xl md:text-4xl font-bold mb-4">
        Next.js + FastAPI App
      </h1>

      <p className="text-gray-600 mb-6 max-w-md">
        Responsive full-stack application with modern technologies.
      </p>

      <Link href="/users">
        <button className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition">
          View Users
        </button>
      </Link>
    </div>
  )
}