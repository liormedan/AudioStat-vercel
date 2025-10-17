import "./globals.css";

export const metadata = {
  title: "BPM Analyzer",
  description: "Upload audio and detect BPM",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="min-h-dvh bg-[var(--bg)] text-[var(--text)]">
        <div className="max-w-3xl mx-auto p-6">
          {children}
        </div>
      </body>
    </html>
  );
}

