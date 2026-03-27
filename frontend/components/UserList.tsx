type User = {
  id: number
  name: string
}

type Props = {
  users: User[]
}

export default function UserList({ users }: Props) {
  if (!users || users.length === 0) {
    return <p className="text-center">No users found.</p>
  }

  return (
    <div className="
      grid gap-4
      grid-cols-1
      sm:grid-cols-2
      lg:grid-cols-3
    ">
      {users.map(user => (
        <div
          key={user.id}
          className="bg-white p-4 rounded-xl shadow hover:shadow-lg transition"
        >
          <h2 className="text-lg font-semibold">{user.name}</h2>
          <p className="text-gray-500 text-sm">User ID: {user.id}</p>
        </div>
      ))}
    </div>
  )
}