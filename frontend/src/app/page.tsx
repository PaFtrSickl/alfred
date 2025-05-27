"use client";

import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Loader2 } from "lucide-react";

interface ClipResponse {
  status: string;
  message: string;
  clip_urls: string[];
  download_all_url: string;
}

const API_BASE_URL = "http://localhost:8000";

export default function Home() {
  const [videoUrl, setVideoUrl] = useState("");
  const [phrase, setPhrase] = useState("");
  const [loading, setLoading] = useState(false);
  const [clips, setClips] = useState<string[]>([]);
  const [error, setError] = useState("");
  const [downloadAllUrl, setDownloadAllUrl] = useState("");
  const [isServerConnected, setIsServerConnected] = useState<boolean | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError("");
    setClips([]);

    try {
      console.log("Sending request to:", `${API_BASE_URL}/clip`);
      const response = await fetch(`${API_BASE_URL}/clip`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Accept": "application/json",
        },
        body: JSON.stringify({
          video_url: videoUrl,
          phrase: phrase,
          before: 2,
          after: 2,
        }),
      });

      if (!response.ok) {
        const errorText = await response.text();
        console.error("Server response:", response.status, errorText);
        try {
          const errorJson = JSON.parse(errorText);
          throw new Error(errorJson.detail || `Server error: ${errorText}`);
        } catch (parseError) {
          if (response.status === 0) {
            throw new Error("Cannot connect to server. Please check if the backend server is running on port 8000.");
          } else if (response.status === 403) {
            throw new Error("CORS error: The backend server needs to allow requests from http://localhost:3000");
          } else {
            throw new Error(`Server responded with ${response.status}: ${errorText}`);
          }
        }
      }

      const data: ClipResponse = await response.json();
      console.log("Received response:", data);

      if (data.status === "error") {
        setError(data.message);
      } else {
        setClips(data.clip_urls);
        setDownloadAllUrl(data.download_all_url);
      }
    } catch (err) {
      console.error("Error details:", err);
      setError(err instanceof Error ? err.message : "Failed to process video. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="container mx-auto px-4 py-8 ">
      <Card className="max-w-2xl mx-auto">
        <CardHeader>
          <CardTitle className="text-3xl font-bold text-center">YouTube Video Clipper</CardTitle>
          <CardDescription className="text-center">
            Search for phrases in YouTube videos and get instant clips
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="space-y-2">
              <label htmlFor="videoUrl" className="text-sm font-medium">
                YouTube URL
              </label>
              <Input
                id="videoUrl"
                type="url"
                placeholder="https://www.youtube.com/watch?v=..."
                value={videoUrl}
                onChange={(e) => setVideoUrl(e.target.value)}
                required
              />
            </div>
            <div className="space-y-2">
              <label htmlFor="phrase" className="text-sm font-medium">
                Search Phrase
              </label>
              <Input
                id="phrase"
                type="text"
                placeholder="Enter the phrase to search for..."
                value={phrase}
                onChange={(e) => setPhrase(e.target.value)}
                required
              />
            </div>
            <Button type="submit" className="w-full" disabled={loading}>
              {loading ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Processing...
                </>
              ) : (
                "Search & Clip"
              )}
            </Button>
          </form>

          {error && (
            <div className="mt-4 p-4 bg-red-50 text-red-600 rounded-md">
              <p className="font-medium">Error:</p>
              <p>{error}</p>
              {error.includes("CORS") && (
                <div className="mt-2 text-sm">
                  <p>To fix CORS issues, make sure your backend server has CORS enabled with:</p>
                  <pre className="mt-1 p-2 bg-gray-100 rounded text-xs overflow-x-auto">
                    {`from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)`}
                  </pre>
                </div>
              )}
            </div>
          )}

          {clips.length > 0 && (
            <div className="mt-8 space-y-4">
              <div className="flex justify-between items-center">
                <h2 className="text-xl font-semibold">Found Clips</h2>
                {downloadAllUrl && (
                  <Button
                    variant="outline"
                    onClick={() => window.open(`${API_BASE_URL}${downloadAllUrl}`, "_blank")}
                  >
                    Download All
                  </Button>
                )}
              </div>
              <div className="grid gap-4">
                {clips.map((clipUrl, index) => (
                  <Card key={index}>
                    <CardContent className="p-4">
                      <video
                        controls
                        className="w-full rounded-lg"
                        src={`${API_BASE_URL}${clipUrl}`}
                      >
                        Your browser does not support the video tag.
                      </video>
                      <div className="mt-2 flex justify-end">
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => {
                            const link = document.createElement('a');
                            link.href = `${API_BASE_URL}${clipUrl}`;
                            // Extract filename from URL or use a default name
                            const filename = clipUrl.split('/').pop() || 'clip.mp4';
                            link.download = filename;
                            document.body.appendChild(link);
                            link.click();
                            document.body.removeChild(link);
                          }}
                        >
                          Download
                        </Button>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            </div>
          )}
        </CardContent>
      </Card>
    </main>
  );
}