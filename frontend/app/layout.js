import { Inter } from "next/font/google";
import "@/styles/globals.css";
import { MainAuthProvider } from "@/lib/authReal";

const inter = Inter({ subsets: ["latin"] });

export const metadata = {
  title: "Checklist App",
  description: "Gerenciador de checklists para processos",
};

export default function RootLayout({ children }) {
  return (
    <html lang="pt-BR">
      <body className={inter.className}>
        <MainAuthProvider>
          {children}
        </MainAuthProvider>
      </body>
    </html>
  );
}