import streamlit as st
import openai

# Set API key
openai.api_key = "your_openai_api_key_here"

# Define function to handle chat with OpenAI
def chat_with_openai(user_input):
    # Create chat completion
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "system", "content": "You are a helpful assistant."},
                  {"role": "user", "content": user_input}]
    )

    # Get response message
    response_message = response['choices'][0]['message']['content']

    # Return response message
    return response_message

# Define function to handle user input
def handle_input():
    # Get user input
    user_input = st.text_input("You:", value="Type your message here...")

    # Check if user has entered a message
    if user_input:
        # Check if user wants to exit chat
        if user_input.lower() == 'exit':
            # Print goodbye message
            st.text("Chatbot: Goodbye!")
        else:
            # Get response from OpenAI chat
            response = chat_with_openai(user_input)

            # Display response from OpenAI
            st.text("Chatbot:" + response)

# Run the app
if __name__ == "__main__":
    st.title("OpenAI Chatbot")
    handle_input()