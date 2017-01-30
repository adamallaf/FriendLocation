package com.saidalattrach.friendlocation;

import android.location.Location;

import org.json.JSONException;
import org.json.JSONObject;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.OutputStream;
import java.net.Socket;

public class Client
{
    public static boolean sendLocationPushQuery(String username, Location location)
    {
        JSONObject locationObject = new JSONObject();
        JSONObject query = new JSONObject();

        try
        {
            locationObject.put("username", username);
            locationObject.put("longitude", location.getLongitude());
            locationObject.put("latitude", location.getLatitude());

            query.put("query", "location_push");
            query.put("location", locationObject);
        } catch (JSONException ignored) {} // This will never happen.. Yeah.. My code is that good

        Socket socket = new Socket();
        try
        {
            OutputStream out = socket.getOutputStream();
            BufferedReader in = new BufferedReader(new InputStreamReader(socket.getInputStream(), "UTF-8"));
            StringBuilder builder = new StringBuilder();

            out.write(query.toString().getBytes("UTF-8"));

            String line = in.readLine();
            while (line != null)
            {
                builder.append(line);
                line = in.readLine();
            }

            try
            {
                JSONObject response = new JSONObject(builder.toString());
                return response.getBoolean("ok");
            }
            catch (JSONException e)
            {
                System.out.println("Response received is in the correct JSON format");
                e.printStackTrace();
                return false;
            }
        }
        catch (IOException e)
        {
            System.out.println("There's a problem with the connection to the server");
            e.printStackTrace();
            return false;
        }
    }
}
