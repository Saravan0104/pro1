import * as React from "react"
import { cn } from "@/lib/utils"

function Card({ className, ...props }) {
  return (
    <div
      className={cn("rounded-xl border bg-white shadow p-4", className)}
      {...props}
    />
  )
}

function CardContent({ className, ...props }) {
  return (
    <div className={cn("text-sm text-gray-700", className)} {...props} />
  )
}

export { Card, CardContent }
