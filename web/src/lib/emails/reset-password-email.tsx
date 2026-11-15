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

interface ResetPasswordEmailProps {
  companyName: string;
  name: string;
  url: string;
}

export const ResetPasswordEmail = ({
  companyName = "AstroPlus",
  name = "Explorer",
  url = "https://example.com/reset",
}: ResetPasswordEmailProps) => {
  return (
    <Html>
      <Head />
      <Preview>Reset your password</Preview>
      <Tailwind>
        <Body className="bg-white my-auto mx-auto font-sans px-2">
          <Container className="border border-solid border-[#eaeaea] rounded my-10 mx-auto p-5 max-w-116.25">
            <Heading className="text-black text-[24px] font-normal text-center p-0 my-7.5 mx-0">
              Reset your password
            </Heading>
            <Text className="text-black text-[14px] leading-6">
              Hello {name},
            </Text>
            <Text className="text-black text-[14px] leading-6">
              We received a request to change your password for{" "}
              {companyName}. You can reset it using the button below:
            </Text>
            <Section className="text-center mt-8 mb-8">
              <Button
                className="bg-[#000000] rounded text-white text-[12px] font-semibold no-underline text-center px-5 py-3"
                href={url}
              >
                Reset Password
              </Button>
            </Section>
            <Text className="text-black text-[14px] leading-6">
              If you did not request this change, please ignore this email. Your
              password will not change until you click the link and set a new
              one.
            </Text>
            <Text className="text-[#666666] text-[12px] leading-6">
              This link will expire in 1 hour.
            </Text>
          </Container>
        </Body>
      </Tailwind>
    </Html>
  );
};

export default ResetPasswordEmail;
