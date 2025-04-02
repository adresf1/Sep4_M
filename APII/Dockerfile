# Brug .NET 9 SDK til at bygge
FROM mcr.microsoft.com/dotnet/sdk:8.0 AS build
WORKDIR /app

# Kopiér og gendan afhængigheder
COPY *.csproj ./
RUN dotnet restore

# Kopiér resten af koden, byg og udgiv
COPY . ./
RUN dotnet publish -c Release -o /out

# Brug .NET 9 runtime til at køre appen
FROM mcr.microsoft.com/dotnet/aspnet:8.0 AS runtime
WORKDIR /app
COPY --from=build /out ./
ENTRYPOINT ["dotnet", "APII.dll"]