import * as React from "react";
import Layout from "../components/layout";
import { graphql } from "gatsby";
import ProfileView from "../components/views/builder/profile";

const ProfilePage = ({ data }: any) => {
  return (
    <Layout meta={data.site.siteMetadata} title="Profile" link={"/profile"}>
      <main style={{ height: "100%" }} className="h-full p-4">
        <ProfileView />
      </main>
    </Layout>
  );
};

export const query = graphql`
  query ProfilePageQuery {
    site {
      siteMetadata {
        description
        title
      }
    }
  }
`;

export default ProfilePage;
