import pyjsonix as pjx 


if __name__ == "__main__":
    json_file_path = "/Users/rishabhvatsa/Desktop/sample_response.json"

    # Reading a single File 
    jf = pjx.read_json(file_paths=json_file_path, fields=["request", "response.email_data.primary_data.key"])

    print(jf.shape)
    print(jf.skeleton)
