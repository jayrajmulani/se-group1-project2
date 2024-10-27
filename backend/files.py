import io
from bson import ObjectId
from flask import request, jsonify, send_file, after_this_request
from pymongo import ReturnDocument
import boto3
import re
import os
from dotenv import load_dotenv
from resume_extract import extract_text_from_pdf

load_dotenv()

s3 = boto3.client('s3', aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
                  aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'))

bucket_name = "job-tracker-resume-upload"


def upload_file(UserRecords, Files):
    
    '''
    ```
    Request:
    {
        email: string,
        start: string,
        file: file,
        end: string,
        filename: string
        
    }
    Response:
    {
        status: 200
        data: Success message
        
        status: 500
        data: Error message
        
    }
    ```
    '''
    
    try:
        file = request.files['file']
        email = str(request.files['email'].read())
        start = email.find("'")
        end = email.rfind("'")
        email = email[start+1:end].strip()
        email_found = UserRecords.find_one({"email": email})
        if email_found:
            _id = str(email_found["_id"])
        else:
            return jsonify({'error': "Email not found"}), 500
        if file:
            filename = _id+"--;--"+file.filename
            file.save(filename)
            s3.upload_file(
                Bucket=bucket_name,
                Filename=filename,
                Key=filename
            )
            Files.insert_one({
                "email": email,
                "filename": filename,
            })
            os.remove(filename)
            return jsonify({"message": "File Uploaded Successfully"}), 200
        else:
            return jsonify({'error': "Found Empty File"}), 500
    except:
        return jsonify({'error': "Something went wrong"}), 500


def view_files(Files):
    
    '''
    ```
    Request:
    {
        email: string  
    }
    Response:
    {
        status: 200
        data: Success message
        
        status: 500
        data: Error message
        
    }
    ```
    '''
    
    try:
        if request:
            email = request.args.get("email")
            out = Files.find({"email": email})
            if out:
                files = []
                for i in out:
                    i['filename'] = i['filename']
                    i['_id'] = str(i['_id'])
                    files.append(i)
                if files:
                    return jsonify({'message': 'Files found', 'files': files}), 200
                else:
                    return jsonify({'message': 'No Files found', 'files': files}), 200
            else:
                return jsonify({'message': 'Email Doesnt Exist'}), 400
    except Exception as e:
        print(e)
        return jsonify({'error': "Something went wrong"}), 500


def generate_cover_letter(Files):
    
    '''
    ```
    Request:
    {
         
    }
    Response:
    {
        status: 200
        data: Success message
        
        status: 500
        data: Error message
        
        status: 400
        data: Error message

        status: 501
        data: Authorization required
        
    }
    ```
    '''
    
    try:
        if request:
            req = request.get_json()
            file = Files.find_one({"filename": req["filename"]})
            if not str(file["filename"]).endswith(".pdf"):
                return jsonify({'message': 'Invalid file type'}), 400
            if file:
                if file["email"] == req["email"]:
                    s3.download_file(
                        bucket_name, file["filename"], req["filename"].split("--;--")[1])
                    # with open("cover_letter.txt", "w+") as f:
                    #     f.write(extract_text_from_pdf(req["filename"].split("--;--")[1]))
                    # return send_file("cover_letter.txt")
                    return send_file(io.BytesIO(extract_text_from_pdf(req["filename"].split("--;--")[1]).encode("utf-8")), 
                                     as_attachment=True, 
                                     download_name="cover_letter.txt", 
                                     mimetype="text/plain")
                else:
                    return jsonify({'message': 'You are not authorized to view this file'}), 501

            return jsonify({'message': 'Files found'}), 200
    except Exception:
        return jsonify({'error': 'Something went wrong'}), 500

def download_file(Files):
    
    '''
    ```
    Request:
    {
         
    }
    Response:
    {
        status: 200
        data: Success message
        
        status: 500
        data: Error message
        
        status: 501
        data: Authorization required
        
    }
    ```
    '''
    
    try:
        if request:
            req = request.get_json()
            file = Files.find_one({"filename": req["filename"]})
            if file:
                if file["email"] == req["email"]:
                    s3.download_file(
                        bucket_name, file["filename"], req["filename"].split("--;--")[1])

                    with open(req["filename"].split("--;--")[1], "rb") as f:
                        file_output = f.read()

                    os.remove(req["filename"].split("--;--")[1])
                    return send_file(io.BytesIO(file_output), 
                                     as_attachment=True, 
                                     download_name=req["filename"].split("--;--")[1])
                else:
                    return jsonify({'message': 'You are not authorized to view this file'}), 501

            return jsonify({'message': 'Files found'}), 200
    except Exception:
        return jsonify({'error': 'Something went wrong'}), 500


def delete_file(Files):
    
    '''
    ```
    Request:
    { 
    }
    Response:
    {
        status: 200
        data: Success message
        
        status: 500
        data: Error message
        
    }
    ```
    '''
    
    try:
        if request:
            req = request.get_json()
            df = Files.find_one_and_delete({"filename": req["filename"]})
            if df == None:
                return jsonify({"error": "No such Job ID found for this user's email"}), 500
            else:
                try:
                    s3.delete_object(Bucket=bucket_name, Key=req["filename"])
                except:
                    pass
                return jsonify({"message": "File Deleted Successfully"}), 200
    except Exception:
        return jsonify({'error': 'Something went wrong'}), 500
