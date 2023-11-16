import React from 'react';
import Link from 'next/link';
import Layout from '../components/Layout';

const Home: React.FC = () => {
  return (
    <Layout>
      <div className="p-4">
        <h1 className="text-3xl font-bold">Welcome to My AI Project</h1>
        <p>Start building your software project with AI assistance.</p>
        <Link href="/dashboard">
          <a className="mt-4 inline-block bg-blue-500 text-white p-2 rounded">
            Go to Dashboard
          </a>
        </Link>
      </div>
    </Layout>
  );
};

export default Home;
