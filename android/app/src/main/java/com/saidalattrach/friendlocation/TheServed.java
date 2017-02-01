package com.saidalattrach.friendlocation;

import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

import java.io.IOException;
import java.io.InputStream;
import java.io.OutputStream;

import java.net.InetSocketAddress;
import java.net.Socket;
import java.net.SocketTimeoutException;

public class TheServed
{
    private static final String HOST = "archoniii.ddns.net";
    private static final int PORT = 30000;
    private static final int TIME_OUT = 15;

    private static final int BUFFER_SIZE = 4096;

    public static boolean sendLocationPushQuery(UserLocation location)
            throws IOException
    {
        JSONObject locationObject = new JSONObject();
        JSONObject query = new JSONObject();

        try
        {
            locationObject.put("username", location.getUsername());
            locationObject.put("longitude", location.getLongitude());
            locationObject.put("latitude", location.getLatitude());

            query.put("query", "location_push");
            query.put("location", locationObject);
        } catch (JSONException ignored) {} // This will never happen.. Yeah.. My code is that good

        JSONObject response = sendQuery(query);
        if (response == null)
            return false;

        try
        {
            return response.getBoolean("ok");
        }
        catch (JSONException e)
        {
            // No error message, because this will never happen
            return false;
        }
    }

    public static UserLocation[] sendLocationPullQuery(String[] usernames) throws IOException
    {
        JSONObject query = new JSONObject();
        JSONArray array = new JSONArray();

        try
        {
            for (String username : usernames)
                array.put(username);

            query.put("query", "location_pull");
            query.put("usernames", array);
        }
        catch (JSONException ignored) {} // This will never happen.. Yeah.. My code is that good

        JSONObject response = sendQuery(query);
        if (response == null)
            return null;
        try
        {
            JSONArray locationsArray = response.getJSONArray("locations");
            UserLocation[] locations = new UserLocation[locationsArray.length()];

            for (int i = 0; i < locations.length; i++)
            {
                JSONObject locationObject = locationsArray.getJSONObject(i);

                String username = locationObject.getString("username");
                double longitude = locationObject.getDouble("longitude");
                double latitude = locationObject.getDouble("latitutde");

                UserLocation location = new UserLocation(username, longitude, latitude);
                locations[i] = location;
            }

            return locations;
        }
        catch (JSONException e)
        {
            System.out.println("Response received is not in the correct JSON format");
            e.printStackTrace();
            return null;
        }
    }

    private static JSONObject sendQuery(JSONObject query)
            throws IOException
    {
        Socket socket = new Socket();

        socket.connect(new InetSocketAddress(HOST, PORT), TIME_OUT);

        OutputStream out = socket.getOutputStream();
        InputStream in = socket.getInputStream();

        out.write(query.toString().getBytes("UTF-8"));

        byte[] buffer = new byte[BUFFER_SIZE];
        in.read(buffer);

        socket.close();

        try
        {
            return new JSONObject(new String(buffer, "UTF-8"));
        }
        catch (JSONException e)
        {
            System.out.println("Response received is not in JSON format");
            e.printStackTrace();
            return null;
        }
    }
}
