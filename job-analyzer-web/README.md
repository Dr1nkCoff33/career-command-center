# Job Market Analyzer Web App

A modern, efficient web application for analyzing resume fit against top tech companies using AI.

## Features

- 🚀 **Fast & Efficient**: Built with Next.js 14 and TypeScript
- 🎨 **Clean UI**: Tailwind CSS with component-specific styles
- 📊 **Visual Results**: Interactive charts showing match scores
- 🔒 **Secure**: API key stored client-side, no server storage
- 📱 **Responsive**: Works on all devices
- 🤖 **AI-Powered**: Uses Claude AI for intelligent analysis

## Tech Stack

- **Frontend**: Next.js 14, React 18, TypeScript
- **Styling**: Tailwind CSS + CSS Modules
- **Charts**: Recharts
- **Icons**: Lucide React
- **AI**: Claude API (Anthropic)

## Getting Started

1. **Install dependencies**:
   ```bash
   cd job-analyzer-web
   npm install
   ```

2. **Run development server**:
   ```bash
   npm run dev
   ```

3. **Open browser**:
   Navigate to http://localhost:3000

## Usage

1. **Optional**: Add your Claude API key for better analysis
2. Upload your resume (PDF, DOC, DOCX, TXT, MD)
3. Select a company (Meta, Apple, Google)
4. Choose locations you're interested in
5. Click "Analyze My Fit"
6. View detailed results with match scores and recommendations

## Deployment

### Vercel (Recommended)

1. Push to GitHub
2. Import project in Vercel
3. Deploy with one click

### Self-hosting

1. Build the project:
   ```bash
   npm run build
   ```

2. Start production server:
   ```bash
   npm start
   ```

### Environment Variables

Create a `.env.local` file:

```env
CLAUDE_API_KEY=your-claude-api-key-here  # Optional
```

## Project Structure

```
job-analyzer-web/
├── src/
│   ├── app/              # Next.js app router
│   │   ├── api/         # API routes
│   │   ├── results/     # Results page
│   │   └── page.tsx     # Home page
│   ├── components/      # React components
│   │   ├── FileUpload/  # Resume upload
│   │   ├── CompanySelector/
│   │   └── ResultsChart/
│   ├── lib/            # Utilities
│   └── types/          # TypeScript types
├── public/             # Static assets
└── package.json
```

## API Endpoints

- `POST /api/analyze`: Analyze resume against selected jobs
  - Body: FormData with resume file, company, locations
  - Returns: Analysis results with match scores

## Security

- No resume data is stored on servers
- API keys are transmitted securely via headers
- All analysis happens in-memory
- Session storage for temporary result display

## Performance

- Efficient CSS with Tailwind utilities
- Component-level code splitting
- Optimized images and assets
- Fast API response times

## Contributing

1. Fork the repository
2. Create feature branch
3. Make changes
4. Submit pull request

## License

MIT