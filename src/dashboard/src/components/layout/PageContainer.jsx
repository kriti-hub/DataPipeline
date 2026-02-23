/**
 * Standard page wrapper with consistent max-width, padding, and spacing.
 */
export default function PageContainer({ children, className = "" }) {
  return (
    <main className={`max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 ${className}`}>
      {children}
    </main>
  );
}
