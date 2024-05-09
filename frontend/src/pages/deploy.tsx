import * as React from "react";
import Layout from "../components/layout";
import { graphql } from "gatsby";
import DeployView from "../components/views/deployment/deploy";

// markup
const IndexPage = ({ data }: any) => {
  return (
    <Layout meta={data.site.siteMetadata} title="Deploy" link={"/deploy"}>
      <main style={{ height: "100%" }} className=" h-full ">
        <DeployView />
      </main>
    </Layout>
  );
};

export const query = graphql`
  query HomePageQuery {
    site {
      siteMetadata {
        description
        title
      }
    }
  }
`;

export default IndexPage;
