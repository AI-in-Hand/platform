import React from "react";
import {graphql} from "gatsby"
import Layout from "../../components/layout";
import Register from "../../components/register";

const RegisterForm = ({ data }: any) => {
    return (
        <Layout meta={data.site.siteMetadata} title="Sign-Up" link={'sing-up'}>
            <Register/>
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

export default RegisterForm;
