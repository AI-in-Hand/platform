import React from 'react';

interface ProjectCardProps {
  title: string;
  description: string;
  // Add other relevant props
}

const ProjectCard: React.FC<ProjectCardProps> = ({ title, description }) => {
  return (
    <div className="border rounded shadow p-4 m-2">
      <h3 className="text-lg font-bold">{title}</h3>
      <p>{description}</p>
      {/* Add more details and action buttons like 'Edit', 'Delete', etc. */}
    </div>
  );
};

export default ProjectCard;
