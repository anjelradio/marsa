import {
  Body,
  Button,
  Container,
  Head,
  Heading,
  Html,
  Preview,
  Section,
  Tailwind,
  Text,
} from "react-email";
import * as React from "react";

interface VerificationEmailProps {
  companyName: string;
  name: string;
  url: string;
}

export const VerificationEmail = ({
  companyName = "AstroPlus",
  name = "Explorer",
  url = "https://example.com/verify",
}: VerificationEmailProps) => {
  return (
    <Html>
      <Head />
      <Preview>Verify your email address</Preview>
      <Tailwind>
        <Body className="bg-white my-auto mx-auto font-sans px-2">
          <Container className="border border-solid border-[#eaeaea] rounded my-10 mx-auto p-5 max-w-116.25">
            <Heading className="text-black text-[24px] font-normal text-center p-0 my-7.5 mx-0">
              Verify your email address
            </Heading>
            <Text className="text-black text-[14px] leading-6">
              Hello {name},
            </Text>
            <Text className="text-black text-[14px] leading-6">
              Thank you for signing up for {companyName}. To complete your
              registration and access your account, please verify your email
              address by clicking the button below.
            </Text>
            <Section className="text-center mt-8 mb-8">
              <Button
                className="bg-[#000000] rounded text-white text-[12px] font-semibold no-underline text-center px-5 py-3"
                href={url}
              >
                Verify Email
              </Button>
            </Section>
            <Text className="text-black text-[14px] leading-6">
              If you did not create an account on {companyName}, you can safely
              ignore this email.
            </Text>
            <Text className="text-[#666666] text-[12px] leading-6">
              This link will expire in 24 hours.
            </Text>
          </Container>
        </Body>
      </Tailwind>
    </Html>
  );
};

export default VerificationEmail;
