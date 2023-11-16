import React, { useEffect, useState } from 'react';
import Layout from '../components/Layout';
import ProjectCard from '../components/ProjectCard';
import useAuth from '../hooks/useAuth';

// Mock data structure for projects
interface Project {
  id: string;
  title: string;
  description: string;
}

const Dashboard: React.FC = () => {
  const { user } = useAuth();
  const [projects, setProjects] = useState<Project[]>([]);

  useEffect(() => {
    // Fetch projects from the backend or Firestore
    // This is a placeholder for demonstration
    setProjects([
      { id: '1', title: 'Project One', description: 'Description for project one.' },
      { id: '2', title: 'Project Two', description: 'Description for project two.' },
      // Add more projects as needed
    ]);
  }, []);

  return (
    <Layout>
      <div className="p-4">
        <h1 className="text-2xl font-bold">Dashboard</h1>
        {user && <p>Welcome, {user.displayName}</p>}
        <div className="mt-4">
          {projects.map((project) => (
            <ProjectCard key={project.id} title={project.title} description={project.description} />
          ))}
        </div>
      </div>
    </Layout>
  );
};

export default Dashboard;
