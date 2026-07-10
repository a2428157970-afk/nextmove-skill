import ResumeUploadCard from "./resume-upload-card";

type BackendStatus = {
  project: string;
  status: string;
};

async function getBackendStatus(): Promise<BackendStatus> {
  const response = await fetch("http://127.0.0.1:8000", {
    cache: "no-store",
  });

  if (!response.ok) {
    throw new Error("Backend request failed");
  }

  return response.json();
}

export default async function Home() {
  const backendStatus = await getBackendStatus();

  return (
    <main className="min-h-screen bg-white px-6 text-zinc-950">
      <div className="mx-auto flex min-h-screen w-full max-w-5xl flex-col justify-between py-10 sm:py-14">
        <Header />
        <Hero backendStatus={backendStatus.status} />
      </div>
    </main>
  );
}

function Header() {
  return (
    <header className="flex items-center justify-between border-b border-zinc-200 pb-5">
      <p className="text-sm font-medium tracking-wide text-zinc-950">
        NextMove
      </p>
      <p className="text-sm text-zinc-500">AI Career Intelligence Platform</p>
    </header>
  );
}

function Hero({ backendStatus }: { backendStatus: string }) {
  return (
    <section className="mx-auto flex w-full max-w-3xl flex-1 flex-col items-center justify-center py-24 text-center">
      <p className="mb-5 text-lg font-medium text-zinc-500">Know Your Value.</p>
      <h1 className="text-5xl font-semibold tracking-normal text-zinc-950 sm:text-6xl">
        NextMove
      </h1>
      <p className="mt-8 text-2xl font-medium text-zinc-800 sm:text-3xl">
        Find Your Next Career Move with AI.
      </p>
      <p className="mt-6 max-w-[640px] text-lg leading-8 text-zinc-500">
        Understand your value, analyze opportunities and make better career
        decisions through AI.
      </p>
      <BackendStatus status={backendStatus} />
      <div className="mt-8 flex flex-col items-center justify-center gap-4 sm:flex-row">
        <button className="h-12 w-64 rounded-md bg-zinc-950 px-6 text-base font-medium text-white transition-colors hover:bg-zinc-800">
          Upload Resume
        </button>
        <button className="h-12 w-64 rounded-md border border-zinc-300 px-6 text-base font-medium text-zinc-950 transition-colors hover:bg-zinc-100">
          Explore Careers
        </button>
      </div>
      <p className="mt-6 text-sm text-zinc-400">
        AI-powered career intelligence for modern professionals.
      </p>
      <ResumeUploadCard />
    </section>
  );
}

function BackendStatus({ status }: { status: string }) {
  const isConnected = status === "running";

  return (
    <p className="mt-7 text-sm font-medium text-zinc-600">
      {isConnected ? (
        <>
          <span aria-hidden="true">&#128994;</span> Backend Connected
        </>
      ) : (
        "Backend Disconnected"
      )}
    </p>
  );
}
